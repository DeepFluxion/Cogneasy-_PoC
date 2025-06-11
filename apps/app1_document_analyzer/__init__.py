"""
App 1: Document Analyzer - NOVA VERSÃO LIMPA
Análise inteligente de documentos médicos
"""

__version__ = "2.0.0"
__app_name__ = "Document Analyzer - Clean"

def is_app1_available():
    """Verifica se App1 está disponível"""
    return True

def is_app1_ready():
    """Verifica se App1 está pronto"""
    return True

def get_app1_status():
    """Retorna status do App1"""
    return {
        "available": True,
        "ready": True,
        "version": __version__,
        "mode": "clean_new"
    }

# Importar função principal
try:
    from .main import run_document_analyzer
    MAIN_AVAILABLE = True
except ImportError:
    MAIN_AVAILABLE = False
    
    def run_document_analyzer():
        import streamlit as st
        st.error("Erro ao carregar App1")

__all__ = [
    "run_document_analyzer",
    "is_app1_available", 
    "is_app1_ready",
    "get_app1_status"
]
