"""
RAG Engine Real - FASE 2C (CORRIGIDO)
Motor completo de Retrieval-Augmented Generation para o App 3
CORREÇÃO: Adicionado método search_documents que estava faltando
"""

import logging
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
import hashlib

try:
    from shared.openai_service_real import get_openai_service
    from shared.chromadb_service import get_chromadb_service
    from shared.sqlite_service import get_sqlite_service
    SERVICES_AVAILABLE = True
except ImportError:
    SERVICES_AVAILABLE = False

logger = logging.getLogger(__name__)

class RAGEngineReal:
    """Motor RAG completo que integra ChromaDB, OpenAI e SQLite"""
    
    def __init__(self):
        self.is_ready = False
        self.stats = {
            "queries_processed": 0,
            "documents_found": 0,
            "successful_responses": 0,
            "errors": 0
        }
        
        if SERVICES_AVAILABLE:
            self._initialize_services()
    
    def _initialize_services(self):
        """Inicializa todos os serviços necessários"""
        try:
            self.openai_service = get_openai_service()
            self.chromadb_service = get_chromadb_service()
            self.sqlite_service = get_sqlite_service()
            
            services_ready = (
                self.openai_service.is_available() and
                self.chromadb_service.is_available() and
                self.sqlite_service.is_available()
            )
            
            if services_ready:
                self.is_ready = True
                logger.info("✅ RAG Engine inicializado")
            else:
                logger.warning("⚠️ RAG Engine com serviços limitados")
                
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar RAG Engine: {e}")
            self.is_ready = False
    
    def is_available(self) -> bool:
        """Verifica se o RAG Engine está pronto para uso"""
        return self.is_ready and SERVICES_AVAILABLE
    
    def search_documents(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """
        MÉTODO CORRIGIDO: Busca documentos na base de conhecimento
        Este método estava faltando e causava o erro: 'RAGEngineReal' object has no attribute 'search_documents'
        """
        if not self.is_available():
            logger.warning("RAG Engine não disponível para busca")
            return {
                "documents": [],
                "total_results": 0,
                "query": query,
                "error": "RAG Engine não disponível"
            }
        
        try:
            # Usar ChromaDB para busca semântica
            results = self.chromadb_service.search_documents(query, max_results)
            
            # Atualizar estatísticas
            self.stats["queries_processed"] += 1
            self.stats["documents_found"] += len(results)
            
            # Enriquecer resultados
            enriched_documents = []
            for result in results:
                enriched_doc = {
                    "content": result["content"],
                    "metadata": result.get("metadata", {}),
                    "similarity": result.get("similarity", 0),
                    "rank": result.get("rank", 0),
                    "document_id": result.get("metadata", {}).get("document_id", "unknown"),
                    "friendly_name": self._get_friendly_name(result.get("metadata", {}).get("document_id", ""))
                }
                enriched_documents.append(enriched_doc)
            
            logger.info(f"Busca realizada: {len(enriched_documents)} documentos encontrados")
            
            return {
                "documents": enriched_documents,
                "total_results": len(enriched_documents),
                "query": query,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro na busca de documentos: {e}")
            self.stats["errors"] += 1
            return {
                "documents": [],
                "total_results": 0,
                "query": query,
                "error": str(e)
            }
    
    def search_knowledge_base(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Busca semântica na base de conhecimento - compatibilidade"""
        result = self.search_documents(query, max_results)
        return result.get("documents", [])
    
    def generate_response(self, question: str, context_documents: List[Dict]) -> Tuple[str, List[str]]:
        """Gera resposta usando RAG completo"""
        if not self.is_available():
            return self._fallback_response(question), []
        
        try:
            # Preparar contexto
            context = self._prepare_context(context_documents)
            
            # Prompt para OpenAI
            prompt = f"""
            Você é um assistente médico especializado em oncologia.
            
            Contexto da base de conhecimento:
            {context}
            
            Pergunta do usuário: {question}
            
            Responda de forma clara, precisa e baseada nas informações fornecidas.
            Se as informações não estiverem no contexto, informe isso claramente.
            Sempre recomende consultar a equipe médica para questões específicas.
            """
            
            # Gerar resposta
            response = self.openai_service.generate_text(
                prompt=prompt,
                max_tokens=800,
                temperature=0.2
            )
            
            # Extrair fontes
            sources = self._extract_sources(context_documents)
            
            self.stats["successful_responses"] += 1
            
            return response, sources
            
        except Exception as e:
            logger.error(f"Erro na geração de resposta: {e}")
            self.stats["errors"] += 1
            return self._fallback_response(question), []
    
    def query_with_sources(self, question: str, max_results: int = 5) -> Dict[str, Any]:
        """Query completo com busca e resposta"""
        start_time = datetime.now()
        
        try:
            # 1. Buscar documentos relevantes
            search_result = self.search_documents(question, max_results)
            documents = search_result.get("documents", [])
            
            if not documents:
                return self._no_context_result(question)
            
            # 2. Gerar resposta com RAG
            response, sources = self.generate_response(question, documents)
            
            # 3. Calcular métricas
            response_time = (datetime.now() - start_time).total_seconds()
            confidence = self._calculate_confidence(documents)
            
            # 4. Salvar no SQLite
            self._save_query_to_sqlite(question, response, sources, confidence)
            
            return {
                "question": question,
                "response": response,
                "sources": sources,
                "relevant_documents": len(documents),
                "response_time": response_time,
                "timestamp": datetime.now().isoformat(),
                "confidence": confidence,
                "document_details": documents[:3]  # Primeiros 3 para detalhes
            }
            
        except Exception as e:
            logger.error(f"Erro na query completa: {e}")
            return self._error_result(question)
    
    def process_medical_query(self, question: str) -> Dict[str, Any]:
        """Processa query médica com RAG completo - nome alternativo para compatibilidade"""
        return self.query_with_sources(question)
    
    def get_knowledge_base_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas da base de conhecimento"""
        try:
            if not self.is_available():
                return {"total_documents": 0, "error": "RAG Engine não disponível"}
            
            # Stats do ChromaDB
            chromadb_stats = self.chromadb_service.get_collection_stats()
            
            # Stats internas
            internal_stats = {
                "rag_engine_stats": self.stats,
                "engine_ready": self.is_ready,
                "services_available": SERVICES_AVAILABLE
            }
            
            return {**chromadb_stats, **internal_stats}
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            return {"total_documents": 0, "error": str(e)}
    
    def _prepare_context(self, documents: List[Dict]) -> str:
        """Prepara contexto para o prompt"""
        if not documents:
            return "Nenhum documento relevante encontrado."
        
        context_parts = []
        for i, doc in enumerate(documents[:5]):  # Máximo 5 documentos
            content = doc.get("content", "")[:500]  # Máximo 500 chars por doc
            source = doc.get("friendly_name", f"Documento {i+1}")
            context_parts.append(f"[{source}]\n{content}\n")
        
        return "\n".join(context_parts)
    
    def _extract_sources(self, documents: List[Dict]) -> List[str]:
        """Extrai lista de fontes dos documentos"""
        sources = []
        for doc in documents:
            friendly_name = doc.get("friendly_name", "")
            if friendly_name and friendly_name not in sources:
                sources.append(friendly_name)
        
        return sources[:5]  # Máximo 5 fontes
    
    def _calculate_confidence(self, documents: List[Dict]) -> float:
        """Calcula confiança baseada na qualidade dos documentos"""
        if not documents:
            return 0.0
        
        # Média das similaridades
        similarities = [doc.get("similarity", 0) for doc in documents]
        avg_similarity = sum(similarities) / len(similarities) if similarities else 0
        
        # Ajustar baseado no número de documentos
        doc_factor = min(len(documents) / 3, 1.0)  # Ideal: 3+ documentos
        
        confidence = avg_similarity * doc_factor
        return min(max(confidence, 0.0), 1.0)  # Entre 0 e 1
    
    def _save_query_to_sqlite(self, question: str, response: str, sources: List[str], confidence: float):
        """Salva query no SQLite para histórico"""
        try:
            if not self.sqlite_service.is_available():
                return
            
            query_data = {
                "question": question,
                "response": response,
                "sources": ",".join(sources),
                "confidence": confidence,
                "app_source": "app3_document_chat",
                "rag_processed": True,
                "timestamp": datetime.now().isoformat()
            }
            
            self.sqlite_service.save_chat_query(query_data)
            
        except Exception as e:
            logger.error(f"Erro ao salvar query: {e}")
    
    def _get_friendly_name(self, document_id: str) -> str:
        """Converte ID do documento para nome amigável"""
        if not document_id:
            return "Documento desconhecido"
        
        # Mapear IDs conhecidos para nomes amigáveis
        friendly_names = {
            "ondasetrona": "Guia de Ondasetrona",
            "quimioterapia": "Manual de Quimioterapia",
            "efeitos_colaterais": "Efeitos Colaterais",
            "cuidados": "Cuidados do Paciente",
            "medicamentos": "Lista de Medicamentos",
            "nutricao": "Guia Nutricional",
            "exercicios": "Exercícios Recomendados",
            "apoio": "Apoio Psicológico"
        }
        
        # Tentar encontrar correspondência
        for key, name in friendly_names.items():
            if key in document_id.lower():
                return name
        
        return f"Documento {document_id[:20]}..."
    
    def _fallback_response(self, question: str) -> str:
        """Resposta de fallback quando IA não está disponível"""
        return f"Não consegui processar sua pergunta sobre '{question}' no momento. Consulte sua equipe médica para dúvidas urgentes."
    
    def _no_context_response(self, question: str) -> str:
        """Resposta sem contexto"""
        return f"Não encontrei informações específicas sobre '{question}' na base atual. Consulte sua equipe médica."
    
    def _error_response(self) -> str:
        """Resposta de erro"""
        return "Erro ao processar consulta. Tente novamente ou consulte sua equipe médica."
    
    def _no_context_result(self, question: str) -> Dict[str, Any]:
        """Resultado sem contexto estruturado"""
        return {
            "question": question,
            "response": self._no_context_response(question),
            "sources": [],
            "relevant_documents": 0,
            "response_time": 0,
            "timestamp": datetime.now().isoformat(),
            "confidence": 0.0,
            "document_details": []
        }
    
    def _error_result(self, question: str) -> Dict[str, Any]:
        """Resultado de erro estruturado"""
        return {
            "question": question,
            "response": self._error_response(),
            "sources": [],
            "relevant_documents": 0,
            "response_time": 0,
            "timestamp": datetime.now().isoformat(),
            "confidence": 0.0,
            "document_details": [],
            "error": True
        }


# Instância singleton
_rag_engine_instance = None

def get_rag_engine() -> RAGEngineReal:
    """Retorna instância singleton do RAG Engine"""
    global _rag_engine_instance
    if _rag_engine_instance is None:
        _rag_engine_instance = RAGEngineReal()
    return _rag_engine_instance

def test_rag_engine() -> Dict[str, Any]:
    """Testa funcionalidades do RAG Engine"""
    engine = get_rag_engine()
    
    results = {
        "engine_available": engine.is_available(),
        "search_test": False,
        "search_documents_test": False,  # Novo teste para método corrigido
        "response_generation": False,
        "complete_query": False,
        "knowledge_stats": False,
        "errors": []
    }
    
    if not engine.is_available():
        results["errors"].append("RAG Engine não disponível")
        return results
    
    try:
        # Teste 1: Busca tradicional
        search_results = engine.search_knowledge_base("ondasetrona efeitos colaterais")
        results["search_test"] = len(search_results) > 0
        
        # Teste 2: Método search_documents (CORRIGIDO)
        search_docs_result = engine.search_documents("ondasetrona efeitos colaterais")
        results["search_documents_test"] = (
            "documents" in search_docs_result and 
            len(search_docs_result["documents"]) > 0
        )
        
        # Teste 3: Geração de resposta
        if search_results:
            response, sources = engine.generate_response("O que é ondasetrona?", search_results)
            results["response_generation"] = len(response) > 50 and len(sources) > 0
        
        # Teste 4: Query completa
        query_result = engine.query_with_sources("Quais são os efeitos colaterais da ondasetrona?")
        results["complete_query"] = "response" in query_result and len(query_result["response"]) > 50
        
        # Teste 5: Estatísticas
        stats = engine.get_knowledge_base_stats()
        results["knowledge_stats"] = "total_documents" in stats
        
    except Exception as e:
        results["errors"].append(str(e))
    
    return results

# Funções de compatibilidade para não quebrar código existente
def search_knowledge_base(question: str, max_results: int = 5) -> List[Dict]:
    """Função de compatibilidade para busca"""
    engine = get_rag_engine()
    return engine.search_knowledge_base(question, max_results)

def generate_rag_response(question: str) -> Tuple[str, List[str]]:
    """Função de compatibilidade para resposta RAG"""
    engine = get_rag_engine()
    
    # Buscar documentos primeiro
    search_result = engine.search_documents(question)
    documents = search_result.get("documents", [])
    
    if not documents:
        return (
            "Não encontrei informações específicas sobre sua pergunta na base de conhecimento. "
            "Recomendo consultar sua equipe médica para esclarecimentos.",
            []
        )
    
    # Gerar resposta
    response, sources = engine.generate_response(question, documents)
    return response, sources

__all__ = [
    "RAGEngineReal", 
    "get_rag_engine", 
    "test_rag_engine",
    "search_knowledge_base",
    "generate_rag_response"
]
    