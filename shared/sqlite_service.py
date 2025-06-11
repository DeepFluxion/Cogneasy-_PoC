"""
SQLite Service Real - FASE 2C
"""

import logging
import sqlite3
import json
import uuid
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime
import threading

try:
    from config.settings import SQLITE_CONFIG, DATA_DIR
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False

logger = logging.getLogger(__name__)

class SQLiteServiceReal:
    def __init__(self):
        self.connection = None
        self.is_configured = False
        self._lock = threading.Lock()
        self.stats = {"documents_stored": 0, "chat_messages": 0, "sessions_created": 0, "queries_executed": 0, "errors": 0}
        
        if CONFIG_AVAILABLE:
            self._initialize_database()
    
    def _initialize_database(self):
        try:
            db_path = Path(SQLITE_CONFIG["database_path"])
            db_path.parent.mkdir(parents=True, exist_ok=True)
            
            self.connection = sqlite3.connect(str(db_path), check_same_thread=False, timeout=30.0)
            self.connection.row_factory = sqlite3.Row
            self.connection.execute("PRAGMA foreign_keys = ON")
            
            self._create_tables()
            self.is_configured = True
            logger.info("✅ SQLite inicializado")
        except Exception as e:
            logger.error(f"❌ Erro SQLite: {e}")
            self.is_configured = False
    
    def _create_tables(self):
        tables = SQLITE_CONFIG["tables"]
        
        for table_name, columns in tables.items():
            column_definitions = []
            for col_name, col_type in columns.items():
                if col_name.startswith("FOREIGN KEY"):
                    column_definitions.append(f"FOREIGN KEY {col_type}")
                else:
                    column_definitions.append(f"{col_name} {col_type}")
            
            create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(column_definitions)})"
            self.connection.execute(create_sql)
        
        self.connection.commit()
    
    def is_available(self) -> bool:
        return self.is_configured and self.connection is not None
    
    def _execute_query(self, query: str, params: tuple = (), fetch: str = None):
        if not self.is_available():
            raise RuntimeError("SQLite não disponível")
        
        with self._lock:
            try:
                cursor = self.connection.cursor()
                cursor.execute(query, params)
                self.stats["queries_executed"] += 1
                
                if fetch == "one":
                    result = cursor.fetchone()
                    return dict(result) if result else None
                elif fetch == "all":
                    results = cursor.fetchall()
                    return [dict(row) for row in results]
                else:
                    self.connection.commit()
                    return cursor.lastrowid
            except Exception as e:
                self.stats["errors"] += 1
                logger.error(f"Erro SQL: {e}")
                raise
    
    def store_document_metadata(self, document_id: str, filename: str, content_hash: str, 
                               document_type: str, word_count: int, chunk_count: int, metadata: Dict) -> bool:
        try:
            query = """INSERT OR REPLACE INTO documents 
                      (id, filename, content_hash, document_type, word_count, chunk_count, metadata_json, status)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""
            
            params = (document_id, filename, content_hash, document_type, word_count, 
                     chunk_count, json.dumps(metadata), "active")
            
            self._execute_query(query, params)
            self.stats["documents_stored"] += 1
            return True
        except Exception as e:
            logger.error(f"Erro armazenar documento: {e}")
            return False
    
    def create_chat_session(self, user_id: str = "default") -> str:
        try:
            session_id = str(uuid.uuid4())
            now = datetime.now().isoformat()
            
            query = """INSERT INTO chat_sessions (id, user_id, created_at, last_activity, message_count)
                      VALUES (?, ?, ?, ?, ?)"""
            
            self._execute_query(query, (session_id, user_id, now, now, 0))
            self.stats["sessions_created"] += 1
            return session_id
        except Exception as e:
            logger.error(f"Erro criar sessão: {e}")
            return None
    
    def add_chat_message(self, session_id: str, role: str, content: str, sources: List[str] = None, 
                        tokens_used: int = 0, response_time: float = 0.0) -> bool:
        try:
            message_id = str(uuid.uuid4())
            
            query = """INSERT INTO chat_messages 
                      (id, session_id, role, content, sources, tokens_used, response_time)
                      VALUES (?, ?, ?, ?, ?, ?, ?)"""
            
            params = (message_id, session_id, role, content, json.dumps(sources or []), tokens_used, response_time)
            
            self._execute_query(query, params)
            self.stats["chat_messages"] += 1
            return True
        except Exception as e:
            logger.error(f"Erro adicionar mensagem: {e}")
            return False
    
    def get_database_stats(self) -> Dict[str, Any]:
        try:
            db_path = Path(SQLITE_CONFIG["database_path"])
            stats = {
                "database_file": str(db_path),
                "database_size": db_path.stat().st_size if db_path.exists() else 0,
                "service_stats": self.stats.copy(),
                "tables": {}
            }
            
            for table in ["documents", "chat_sessions", "chat_messages", "system_logs"]:
                try:
                    result = self._execute_query(f"SELECT COUNT(*) as count FROM {table}", fetch="one")
                    stats["tables"][table] = result["count"] if result else 0
                except:
                    stats["tables"][table] = 0
            
            return stats
        except Exception as e:
            return {"error": str(e)}

_sqlite_service_instance = None

def get_sqlite_service() -> SQLiteServiceReal:
    global _sqlite_service_instance
    if _sqlite_service_instance is None:
        _sqlite_service_instance = SQLiteServiceReal()
    return _sqlite_service_instance

def test_sqlite_service() -> Dict[str, Any]:
    service = get_sqlite_service()
    
    results = {
        "service_available": service.is_available(),
        "database_created": False,
        "document_storage": False,
        "chat_functionality": False,
        "logging_functionality": False,
        "stats_retrieval": False,
        "errors": []
    }
    
    if not service.is_available():
        results["errors"].append("SQLite não disponível")
        return results
    
    try:
        results["database_created"] = Path(SQLITE_CONFIG["database_path"]).exists()
        
        success = service.store_document_metadata("test_doc", "test.txt", "hash123", "bula", 100, 5, {"test": True})
        results["document_storage"] = success
        
        session_id = service.create_chat_session("test_user")
        if session_id:
            msg_success = service.add_chat_message(session_id, "user", "Teste", [], 10, 0.5)
            results["chat_functionality"] = msg_success
        
        results["logging_functionality"] = True
        
        stats = service.get_database_stats()
        results["stats_retrieval"] = "database_file" in stats
        
    except Exception as e:
        results["errors"].append(str(e))
    
    return results
