"""
ChromaDB Service Real - FASE 2C (CORRIGIDO)
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple
from datetime import datetime

try:
    import chromadb
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

try:
    from config.settings import CHROMADB_CONFIG, VECTOR_STORES_DIR
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False

logger = logging.getLogger(__name__)

class ChromaDBServiceReal:
    def __init__(self):
        self.client = None
        self.collection = None
        self.is_configured = False
        self.stats = {"documents_added": 0, "searches_performed": 0}
        
        if CHROMADB_AVAILABLE and CONFIG_AVAILABLE:
            self._initialize_client()
    
    def _initialize_client(self):
        try:
            persist_dir = Path(CHROMADB_CONFIG["persist_directory"])
            persist_dir.mkdir(parents=True, exist_ok=True)
            
            self.client = chromadb.PersistentClient(path=str(persist_dir))
            self._setup_collection()
            self.is_configured = True
            logger.info("✅ ChromaDB inicializado")
        except Exception as e:
            logger.error(f"❌ Erro ChromaDB: {e}")
            self.is_configured = False
    
    def _setup_collection(self):
        try:
            collection_name = CHROMADB_CONFIG["collection_name"]
            try:
                self.collection = self.client.get_collection(name=collection_name)
            except:
                self.collection = self.client.create_collection(name=collection_name)
        except Exception as e:
            logger.error(f"Erro coleção: {e}")
    
    def is_available(self) -> bool:
        return self.is_configured and self.collection is not None
    
    def add_document(self, document_id: str, content: str, metadata: Dict = None) -> bool:
        if not self.is_available():
            return False
        
        try:
            chunks = [content[i:i+1000] for i in range(0, len(content), 800)]
            chunk_ids = [f"{document_id}_chunk_{i}" for i in range(len(chunks))]
            metadatas = [{"document_id": document_id, "chunk_index": i, **(metadata or {})} 
                        for i in range(len(chunks))]
            
            self.collection.add(ids=chunk_ids, documents=chunks, metadatas=metadatas)
            self.stats["documents_added"] += 1
            
            logger.info(f"✅ Documento adicionado: {document_id}")
            return True
        except Exception as e:
            logger.error(f"Erro adicionar documento: {e}")
            return False
    
    def search_documents(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """CORREÇÃO: Retorna apenas lista de documentos"""
        if not self.is_available():
            return []
        
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=max_results,
                include=["documents", "metadatas", "distances"]
            )
            
            documents = []
            if results["documents"] and len(results["documents"]) > 0:
                for i, (doc, metadata, distance) in enumerate(zip(
                    results["documents"][0],
                    results["metadatas"][0], 
                    results["distances"][0]
                )):
                    documents.append({
                        "content": doc,
                        "metadata": metadata,
                        "similarity": 1 - distance,
                        "rank": i + 1
                    })
            
            self.stats["searches_performed"] += 1
            return documents
        except Exception as e:
            logger.error(f"Erro busca: {e}")
            return []
    
    def get_document_sources(self, search_results: List[Dict]) -> List[str]:
        sources = []
        seen_docs = set()
        
        for result in search_results:
            metadata = result.get("metadata", {})
            doc_id = metadata.get("document_id", "Documento")
            
            if doc_id not in seen_docs:
                sources.append(doc_id.replace('_', ' ').title())
                seen_docs.add(doc_id)
        
        return sources
    
    def get_collection_stats(self) -> Dict[str, Any]:
        if not self.is_available():
            return {"available": False, "error": "ChromaDB não disponível"}
        
        try:
            count = self.collection.count()
            sample = self.collection.get(limit=10, include=["metadatas"])
            
            unique_docs = set()
            friendly_names = []
            
            if sample and sample["metadatas"]:
                for metadata in sample["metadatas"]:
                    doc_id = metadata.get("document_id", "")
                    if doc_id and doc_id not in unique_docs:
                        unique_docs.add(doc_id)
                        friendly_name = doc_id.replace('_', ' ').title()
                        if "ondasetrona" in doc_id.lower():
                            friendly_name = "Bula - Ondasetrona 8mg"
                        elif "dexametasona" in doc_id.lower():
                            friendly_name = "Bula - Dexametasona 4mg"
                        elif "metoclopramida" in doc_id.lower():
                            friendly_name = "Bula - Metoclopramida 10mg"
                        elif "quimioterapia" in doc_id.lower():
                            friendly_name = "Orientações - Quimioterapia"
                        elif "alimentacao" in doc_id.lower():
                            friendly_name = "Guia - Alimentação"
                        elif "alerta" in doc_id.lower():
                            friendly_name = "Protocolo - Sinais de Alerta"
                        elif "cateter" in doc_id.lower():
                            friendly_name = "Cuidados - Cateter"
                        elif "apoio" in doc_id.lower():
                            friendly_name = "Guia - Apoio Emocional"
                        
                        friendly_names.append(friendly_name)
            
            return {
                "available": True,
                "collection_name": CHROMADB_CONFIG["collection_name"],
                "total_chunks": count,
                "total_documents": len(unique_docs),
                "friendly_names": friendly_names,
                "documents_with_names": [{"id": doc, "friendly_name": name, 
                                        "filename": f"{doc}.txt", "document_type": "documento"} 
                                       for doc, name in zip(unique_docs, friendly_names)]
            }
        except Exception as e:
            return {"available": False, "error": str(e)}

_chromadb_service_instance = None

def get_chromadb_service() -> ChromaDBServiceReal:
    global _chromadb_service_instance
    if _chromadb_service_instance is None:
        _chromadb_service_instance = ChromaDBServiceReal()
    return _chromadb_service_instance

def test_chromadb_service() -> Dict[str, Any]:
    service = get_chromadb_service()
    
    results = {
        "service_available": service.is_available(),
        "collection_created": False,
        "document_add": False,
        "search_functionality": False,
        "stats_retrieval": False,
        "errors": []
    }
    
    if not service.is_available():
        results["errors"].append("ChromaDB não disponível")
        return results
    
    try:
        stats = service.get_collection_stats()
        results["collection_created"] = stats.get("available", False)
        results["stats_retrieval"] = True
        
        success = service.add_document("test_doc", "Teste ChromaDB", {"type": "test"})
        results["document_add"] = success
        
        if success:
            search_results = service.search_documents("teste")
            results["search_functionality"] = len(search_results) > 0
            
    except Exception as e:
        results["errors"].append(str(e))
    
    return results
