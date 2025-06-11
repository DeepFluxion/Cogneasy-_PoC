'''
App 3: Document Chat - Integração Real FASE 2C
'''

import streamlit as st
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

APP_INFO = {
    "name": "Document Chat - RAG Real",
    "version": "2C.1.0",
    "description": "Chat com RAG real usando infraestrutura FASE 2C",
    "status": "production_ready"
}

def check_dependencies() -> dict:
    '''Verifica dependências do App 3 real'''
    deps = {
        "openai_service": False,
        "chromadb_service": False,
        "rag_engine": False,
        "chat_manager": False
    }
    
    try:
        from shared.openai_service_real import get_openai_service
        deps["openai_service"] = get_openai_service().is_available()
        
        from shared.chromadb_service import get_chromadb_service
        deps["chromadb_service"] = get_chromadb_service().is_available()
        
        from .rag_engine import get_rag_engine
        deps["rag_engine"] = get_rag_engine().is_available()
        
        from .chat_manager import get_chat_manager
        deps["chat_manager"] = get_chat_manager().is_available()
        
    except Exception as e:
        logger.error(f"Erro ao verificar dependências: {e}")
    
    return deps

def validate_app3_readiness() -> dict:
    '''Valida se App 3 está pronto'''
    
    deps = check_dependencies()
    critical_services = ["openai_service", "chromadb_service", "rag_engine"]
    critical_ready = all(deps.get(service, False) for service in critical_services)
    
    # Verificar base
    docs_count = 0
    try:
        if deps["rag_engine"]:
            from .rag_engine import get_rag_engine
            stats = get_rag_engine().get_knowledge_base_stats()
            docs_count = stats.get("total_documents", 0)
    except:
        pass
    
    kb_ready = docs_count > 0
    
    if critical_ready and kb_ready:
        status = "ready"
        message = "App 3 totalmente funcional com RAG real"
    elif critical_ready:
        status = "partial"
        message = "App 3 funcional, base limitada"
    else:
        status = "limited"
        message = "App 3 em modo limitado"
    
    return {
        "status": status,
        "message": message,
        "critical_ready": critical_ready,
        "kb_ready": kb_ready,
        "docs_count": docs_count,
        "dependencies": deps
    }

def main():
    '''Função principal do App 3'''
    try:
        from .main import main as app3_main
        app3_main()
    except Exception as e:
        st.error(f"Erro: {e}")

__all__ = ["check_dependencies", "validate_app3_readiness", "main"]
