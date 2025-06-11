'''
Chat Manager Real - FASE 2C
'''

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

try:
    from .rag_engine import get_rag_engine
    from shared.sqlite_service import get_sqlite_service
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False

logger = logging.getLogger(__name__)

class ChatManagerReal:
    '''Gerenciador de chat que coordena conversas e RAG'''
    
    def __init__(self):
        self.is_ready = False
        self.sessions = {}
        self.stats = {"total_messages": 0, "successful_queries": 0, "active_sessions": 0, "errors": 0}
        
        if RAG_AVAILABLE:
            self._initialize_services()
    
    def _initialize_services(self):
        '''Inicializa serviços necessários'''
        try:
            self.rag_engine = get_rag_engine()
            self.sqlite_service = get_sqlite_service()
            
            if self.rag_engine.is_available() and self.sqlite_service.is_available():
                self.is_ready = True
                logger.info("✅ Chat Manager inicializado")
            else:
                logger.warning("⚠️ Chat Manager limitado")
                
        except Exception as e:
            logger.error(f"❌ Erro Chat Manager: {e}")
            self.is_ready = False
    
    def is_available(self) -> bool:
        '''Verifica se está pronto'''
        return self.is_ready and RAG_AVAILABLE
    
    def create_session(self, user_id: str = "default") -> str:
        '''Cria nova sessão'''
        try:
            if self.sqlite_service.is_available():
                session_id = self.sqlite_service.create_chat_session(user_id)
            else:
                session_id = str(uuid.uuid4())
            
            self.sessions[session_id] = {
                "created_at": datetime.now(),
                "user_id": user_id,
                "message_count": 0,
                "last_activity": datetime.now(),
                "context": []
            }
            
            self.stats["active_sessions"] += 1
            return session_id
            
        except Exception as e:
            logger.error(f"Erro criar sessão: {e}")
            return str(uuid.uuid4())
    
    def send_message(self, session_id: str, message: str, message_type: str = "user") -> Dict[str, Any]:
        '''Envia mensagem e processa resposta'''
        try:
            if session_id not in self.sessions:
                return self._error_response("Sessão não encontrada")
            
            self.sessions[session_id]["last_activity"] = datetime.now()
            self.sessions[session_id]["message_count"] += 1
            
            if message_type == "user":
                response = self._process_user_message(session_id, message)
            else:
                response = {"message": message, "type": message_type}
            
            self._add_to_context(session_id, message, message_type)
            if message_type == "user" and "response" in response:
                self._add_to_context(session_id, response["response"], "assistant")
            
            self.stats["total_messages"] += 1
            return response
            
        except Exception as e:
            logger.error(f"Erro processar mensagem: {e}")
            return self._error_response("Erro interno")
    
    def _process_user_message(self, session_id: str, message: str) -> Dict[str, Any]:
        '''Processa mensagem usando RAG'''
        if not self.rag_engine.is_available():
            return self._fallback_response(message)
        
        try:
            rag_result = self.rag_engine.process_medical_query(message, session_id)
            
            if "error" in rag_result:
                return self._error_response("Erro ao processar consulta")
            
            response = {
                "message": message,
                "response": rag_result["response"],
                "sources": rag_result["sources"],
                "type": "medical_query",
                "timestamp": rag_result["timestamp"],
                "confidence": rag_result["confidence"],
                "response_time": rag_result["response_time"],
                "relevant_documents": rag_result["relevant_documents"],
                "document_details": rag_result.get("document_details", [])
            }
            
            self.stats["successful_queries"] += 1
            return response
            
        except Exception as e:
            logger.error(f"Erro RAG: {e}")
            return self._error_response("Erro na consulta")
    
    def get_session_history(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        '''Recupera histórico'''
        try:
            if session_id not in self.sessions:
                return []
            
            context = self.sessions[session_id].get("context", [])
            return context[-limit:] if limit else context
            
        except Exception as e:
            logger.error(f"Erro histórico: {e}")
            return []
    
    def get_available_documents(self) -> List[Dict[str, Any]]:
        '''Lista documentos disponíveis'''
        try:
            if not self.rag_engine.is_available():
                return []
            
            stats = self.rag_engine.get_knowledge_base_stats()
            
            documents = []
            for doc_name in stats.get("available_documents", []):
                documents.append({
                    "name": doc_name,
                    "type": "knowledge_base",
                    "available": True
                })
            
            return documents
            
        except Exception as e:
            logger.error(f"Erro listar docs: {e}")
            return []
    
    def get_suggested_questions(self) -> List[str]:
        '''Perguntas sugeridas'''
        return [
            "Quais são os efeitos colaterais da ondasetrona?",
            "Como me preparar para quimioterapia?",
            "Que alimentos posso comer?",
            "Quando procurar emergência?",
            "Como cuidar do cateter?",
            "Dosagem da dexametasona?",
            "Metoclopramida com outros medicamentos?",
            "Apoio emocional no tratamento?",
            "Sinais de alerta?",
            "Alimentação durante quimio?"
        ]
    
    def get_manager_stats(self) -> Dict[str, Any]:
        '''Estatísticas do manager'''
        return {
            "chat_manager_ready": self.is_ready,
            "active_sessions": len(self.sessions),
            "stats": self.stats.copy(),
            "rag_engine_available": self.rag_engine.is_available() if hasattr(self, 'rag_engine') else False
        }
    
    def _add_to_context(self, session_id: str, message: str, message_type: str):
        '''Adiciona ao contexto'''
        try:
            if session_id in self.sessions:
                self.sessions[session_id]["context"].append({
                    "message": message,
                    "type": message_type,
                    "timestamp": datetime.now().isoformat()
                })
                
                if len(self.sessions[session_id]["context"]) > 100:
                    self.sessions[session_id]["context"] = self.sessions[session_id]["context"][-100:]
                    
        except Exception as e:
            logger.error(f"Erro contexto: {e}")
    
    def _fallback_response(self, message: str) -> Dict[str, Any]:
        '''Resposta fallback'''
        return {
            "message": message,
            "response": "Sistema indisponível. Consulte sua equipe médica para dúvidas urgentes.",
            "sources": [],
            "type": "fallback",
            "timestamp": datetime.now().isoformat(),
            "confidence": 0.0,
            "response_time": 0,
            "relevant_documents": 0
        }
    
    def _error_response(self, error_msg: str) -> Dict[str, Any]:
        '''Resposta de erro'''
        return {
            "message": "",
            "response": f"Erro: {error_msg}. Consulte sua equipe médica para dúvidas urgentes.",
            "sources": [],
            "type": "error",
            "timestamp": datetime.now().isoformat(),
            "confidence": 0.0,
            "response_time": 0,
            "relevant_documents": 0,
            "error": True
        }

_chat_manager_instance = None

def get_chat_manager() -> ChatManagerReal:
    '''Instância singleton'''
    global _chat_manager_instance
    if _chat_manager_instance is None:
        _chat_manager_instance = ChatManagerReal()
    return _chat_manager_instance

def test_chat_manager() -> Dict[str, Any]:
    '''Testa Chat Manager'''
    manager = get_chat_manager()
    
    results = {
        "manager_available": manager.is_available(),
        "session_creation": False,
        "message_processing": False,
        "document_listing": False,
        "history_retrieval": False,
        "errors": []
    }
    
    if not manager.is_available():
        results["errors"].append("Chat Manager não disponível")
        return results
    
    try:
        session_id = manager.create_session("test_user")
        results["session_creation"] = bool(session_id)
        
        if session_id:
            response = manager.send_message(session_id, "O que é ondasetrona?")
            results["message_processing"] = "response" in response and len(response["response"]) > 10
        
        documents = manager.get_available_documents()
        results["document_listing"] = len(documents) > 0
        
        if session_id:
            history = manager.get_session_history(session_id)
            results["history_retrieval"] = isinstance(history, list)
        
    except Exception as e:
        results["errors"].append(str(e))
    
    return results
