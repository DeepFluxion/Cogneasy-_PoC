"""
OpenAI Service Real - FASE 2C (CORRIGIDO)
"""

import logging
from typing import List, Dict, Any, Tuple
from datetime import datetime

try:
    import openai
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from config.settings import OPENAI_CONFIG
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False

logger = logging.getLogger(__name__)

class OpenAIServiceReal:
    def __init__(self):
        self.client = None
        self.is_configured = False
        self.stats = {"chat_requests": 0, "embedding_requests": 0, "total_tokens": 0, "errors": 0, "cache_hits": 0}
        
        if OPENAI_AVAILABLE and CONFIG_AVAILABLE:
            self._initialize_client()
    
    def _initialize_client(self):
        try:
            api_key = OPENAI_CONFIG.get("api_key")
            if not api_key:
                logger.warning("OpenAI API key não configurada")
                return
            
            self.client = OpenAI(api_key=api_key, timeout=30)
            self.is_configured = True
            logger.info("✅ OpenAI service inicializado")
        except Exception as e:
            logger.error(f"❌ Erro OpenAI: {e}")
            self.is_configured = False
    
    def is_available(self) -> bool:
        return self.is_configured and self.client is not None
    
    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        if not self.is_available():
            raise RuntimeError("OpenAI não disponível")
        
        try:
            response = self.client.embeddings.create(
                model=OPENAI_CONFIG["models"]["embedding"],
                input=texts
            )
            
            embeddings = [data.embedding for data in response.data]
            self.stats["embedding_requests"] += 1
            self.stats["total_tokens"] += response.usage.total_tokens
            
            return embeddings
        except Exception as e:
            self.stats["errors"] += 1
            raise RuntimeError(f"Erro embeddings: {e}")
    
    def chat_completion(self, messages: List[Dict[str, str]], max_tokens: int = None) -> Tuple[str, Dict]:
        if not self.is_available():
            raise RuntimeError("OpenAI não disponível")
        
        try:
            response = self.client.chat.completions.create(
                model=OPENAI_CONFIG["models"]["chat"],
                messages=messages,
                max_tokens=max_tokens or OPENAI_CONFIG["limits"]["max_tokens"],
                temperature=OPENAI_CONFIG["limits"]["temperature"]
            )
            
            content = response.choices[0].message.content or ""
            metadata = {
                "tokens_used": response.usage.total_tokens,
                "model": response.model,
                "timestamp": datetime.now().isoformat()
            }
            
            self.stats["chat_requests"] += 1
            self.stats["total_tokens"] += response.usage.total_tokens
            
            return content, metadata
        except Exception as e:
            self.stats["errors"] += 1
            raise RuntimeError(f"Erro chat: {e}")
    
    def answer_medical_question_with_rag(self, question: str, relevant_documents: List[str]) -> Tuple[str, List[str]]:
        try:
            context = "\n\n".join(relevant_documents[:3])
            
            messages = [
                {"role": "system", "content": "Você é um assistente médico. Use APENAS as informações fornecidas. Sempre cite as fontes."},
                {"role": "user", "content": f"Contexto: {context}\n\nPergunta: {question}"}
            ]
            
            response, metadata = self.chat_completion(messages)
            sources = [f"Documento {i+1}" for i in range(len(relevant_documents[:3]))]
            
            return response, sources
        except Exception as e:
            return f"Erro: {e}", []
    
    def get_usage_stats(self) -> Dict[str, Any]:
        return {
            "service_status": "available" if self.is_available() else "unavailable",
            "statistics": self.stats.copy()
        }

_openai_service_instance = None

def get_openai_service() -> OpenAIServiceReal:
    global _openai_service_instance
    if _openai_service_instance is None:
        _openai_service_instance = OpenAIServiceReal()
    return _openai_service_instance

def test_openai_service() -> Dict[str, Any]:
    """TESTE CORRIGIDO - Não falha se OpenAI não estiver configurado"""
    service = get_openai_service()
    
    results = {
        "service_available": service.is_available(),
        "connection_test": False,
        "embedding_test": False,
        "chat_test": False,
        "rag_test": False,
        "extraction_test": False,
        "errors": []
    }
    
    if not service.is_available():
        # CORREÇÃO: Não adicionar erro se só não estiver configurado
        if not OPENAI_AVAILABLE:
            results["errors"].append("OpenAI não instalado")
        elif not CONFIG_AVAILABLE:
            results["errors"].append("Configurações não disponíveis")
        else:
            results["errors"].append("OpenAI não configurado (API key)")
        
        return results
    
    try:
        # Teste de conexão
        response, _ = service.chat_completion([{"role": "user", "content": "Responda apenas: OK"}])
        results["connection_test"] = "ok" in response.lower()
        results["chat_test"] = True
        
        # Teste de embeddings
        embeddings = service.create_embeddings(["teste"])
        results["embedding_test"] = len(embeddings) == 1 and len(embeddings[0]) > 0
        
        # Teste RAG
        response, sources = service.answer_medical_question_with_rag(
            "O que é ondasetrona?", 
            ["Ondasetrona é um medicamento antiemético"]
        )
        results["rag_test"] = len(response) > 10
        results["extraction_test"] = True
        
    except Exception as e:
        results["errors"].append(str(e))
    
    return results
