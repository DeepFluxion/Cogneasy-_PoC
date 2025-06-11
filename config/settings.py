"""
Configurações principais do CognEasy PoCs - FASE 2C
OpenAI obrigatória, ChromaDB real, SQLite real
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Diretórios base
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
KNOWLEDGE_BASE_DIR = DATA_DIR / "knowledge_base"
VECTOR_STORES_DIR = DATA_DIR / "vector_stores" 
SQLITE_DB_PATH = DATA_DIR / "cogneasy_real.db"

# Cria diretórios se não existirem
DATA_DIR.mkdir(exist_ok=True)
KNOWLEDGE_BASE_DIR.mkdir(exist_ok=True)
VECTOR_STORES_DIR.mkdir(exist_ok=True)

# OpenAI API Key - OBRIGATÓRIA na FASE 2C
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")

# Validação da OpenAI
if not OPENAI_API_KEY:
    print("❌ ERRO: OPENAI_API_KEY não configurada!")
    print("🔧 Configure no arquivo .env: OPENAI_API_KEY=sua-chave-aqui")
else:
    print(f"✅ OpenAI configurada: {OPENAI_API_KEY[:8]}...{OPENAI_API_KEY[-4:]}")

# Configurações OpenAI
OPENAI_CONFIG = {
    "api_key": OPENAI_API_KEY,
    "api_base": OPENAI_API_BASE,
    "models": {
        "chat": "gpt-3.5-turbo",
        "embedding": "text-embedding-3-small",
        "fallback": "gpt-3.5-turbo"
    },
    "limits": {
        "max_tokens": 1000,
        "temperature": 0.1,
        "max_retries": 3,
        "timeout": 30,
        "rate_limit_delay": 1
    },
    "embedding_config": {
        "chunk_size": 1000,
        "chunk_overlap": 200,
        "max_chunks_per_doc": 50,
        "batch_size": 10
    }
}

# Configurações ChromaDB
CHROMADB_CONFIG = {
    "persist_directory": str(VECTOR_STORES_DIR),
    "collection_name": "cogneasy_medical_docs_v2c",
    "embedding_function": "openai",
    "distance_metric": "cosine",
    "settings": {
        "anonymized_telemetry": False,
        "allow_reset": True,
        "is_persistent": True
    },
    "search_config": {
        "max_results": 5,
        "min_similarity": 0.3,
        "include_metadata": True,
        "include_distances": True
    }
}

# Configurações SQLite
SQLITE_CONFIG = {
    "database_path": str(SQLITE_DB_PATH),
    "tables": {
        "documents": {
            "id": "TEXT PRIMARY KEY",
            "filename": "TEXT NOT NULL",
            "content_hash": "TEXT UNIQUE",
            "document_type": "TEXT",
            "upload_timestamp": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "word_count": "INTEGER",
            "chunk_count": "INTEGER", 
            "metadata_json": "TEXT",
            "status": "TEXT DEFAULT 'active'"
        },
        "chat_sessions": {
            "id": "TEXT PRIMARY KEY",
            "user_id": "TEXT",
            "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "last_activity": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "message_count": "INTEGER DEFAULT 0",
            "status": "TEXT DEFAULT 'active'"
        },
        "chat_messages": {
            "id": "TEXT PRIMARY KEY",
            "session_id": "TEXT",
            "role": "TEXT NOT NULL",
            "content": "TEXT NOT NULL",
            "sources": "TEXT",
            "timestamp": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "tokens_used": "INTEGER",
            "response_time": "REAL"
        },
        "system_logs": {
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "level": "TEXT NOT NULL",
            "component": "TEXT NOT NULL",
            "message": "TEXT NOT NULL",
            "details_json": "TEXT",
            "timestamp": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        }
    }
}

# Configurações da base de conhecimento
KNOWLEDGE_BASE_CONFIG = {
    "documents_directory": str(KNOWLEDGE_BASE_DIR),
    "supported_formats": [".txt", ".pdf", ".docx"],
    "auto_load_on_startup": True,
    "required_documents": [
        "ondasetrona_8mg_bula.txt",
        "dexametasona_4mg_bula.txt", 
        "metoclopramida_10mg_bula.txt",
        "orientacoes_quimioterapia.txt",
        "guia_alimentacao_oncologica.txt",
        "sinais_alerta_emergencia.txt",
        "cuidados_cateter_venoso.txt",
        "apoio_emocional_paciente.txt"
    ],
    "validation": {
        "min_word_count": 100,
        "require_medical_terms": True,
        "check_duplicates": True
    }
}

# Configurações dos apps
APP_CONFIGS = {
    "app1_document_analyzer": {
        "max_file_size": 10 * 1024 * 1024,
        "supported_types": ["pdf", "txt", "docx", "jpg", "png"],
        "openai_extraction": True,
        "save_extractions": True
    },
    "app2_smart_scheduler": {
        "openai_function_calling": True,
        "calendar_integration": True,
        "save_events": True
    },
    "app3_document_chat": {
        "use_real_rag": True,
        "openai_chat": True,
        "require_sources": True,
        "save_conversations": True,
        "max_conversation_length": 20
    }
}

# Configurações de sistema
SYSTEM_CONFIG = {
    "phase": "2C",
    "require_openai": True,
    "require_chromadb": True,
    "fallback_mode": False,
    "debug_mode": os.getenv("DEBUG", "false").lower() == "true",
    "log_level": os.getenv("LOG_LEVEL", "INFO"),
    "performance_monitoring": True,
    "startup_validation": True
}

def validate_phase2c_requirements():
    """Valida se todos os requisitos da FASE 2C estão atendidos"""
    
    issues = []
    
    # Validar OpenAI
    if not OPENAI_API_KEY:
        issues.append("OpenAI API Key não configurada")
    
    # Validar diretórios
    for directory in [DATA_DIR, KNOWLEDGE_BASE_DIR, VECTOR_STORES_DIR]:
        if not directory.exists():
            try:
                directory.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                issues.append(f"Não foi possível criar diretório {directory}: {e}")
    
    # Validar dependências críticas
    try:
        import openai
        import chromadb
        import sqlite3
    except ImportError as e:
        issues.append(f"Dependência não instalada: {e}")
    
    return len(issues) == 0, issues

def get_phase2c_status():
    """Retorna status completo da FASE 2C"""
    
    is_valid, issues = validate_phase2c_requirements()
    
    status = {
        "phase": "2C",
        "mode": "real_apis_only",
        "openai_configured": bool(OPENAI_API_KEY),
        "directories_ready": all(d.exists() for d in [DATA_DIR, KNOWLEDGE_BASE_DIR, VECTOR_STORES_DIR]),
        "validation_passed": is_valid,
        "issues": issues,
        "config": {
            "openai_model": OPENAI_CONFIG["models"]["chat"],
            "embedding_model": OPENAI_CONFIG["models"]["embedding"],
            "chromadb_collection": CHROMADB_CONFIG["collection_name"],
            "sqlite_database": SQLITE_CONFIG["database_path"],
            "knowledge_base_docs": len(KNOWLEDGE_BASE_CONFIG["required_documents"])
        }
    }
    
    return status

# Executar validação na importação (só avisos)
if __name__ != "__main__":
    try:
        _is_valid, _issues = validate_phase2c_requirements()
        if not _is_valid:
            print("⚠️  AVISOS FASE 2C:")
            for issue in _issues:
                print(f"   • {issue}")
    except Exception:
        pass  # Ignorar erros durante import

# Debug info
if SYSTEM_CONFIG["debug_mode"]:
    print(f"🔧 DEBUG FASE 2C:")
    print(f"   OpenAI: {OPENAI_CONFIG['models']['chat']}")
    print(f"   ChromaDB: {CHROMADB_CONFIG['collection_name']}")
    print(f"   SQLite: {SQLITE_CONFIG['database_path']}")
    print(f"   Base: {len(KNOWLEDGE_BASE_CONFIG['required_documents'])} docs")

# Exportações principais
__all__ = [
    "OPENAI_CONFIG", "CHROMADB_CONFIG", "SQLITE_CONFIG", 
    "KNOWLEDGE_BASE_CONFIG", "APP_CONFIGS", "SYSTEM_CONFIG",
    "validate_phase2c_requirements", "get_phase2c_status"
]