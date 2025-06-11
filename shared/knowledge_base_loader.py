"""
Knowledge Base Loader - FASE 2C
"""

import logging
from pathlib import Path
from typing import Dict, List, Tuple, Any
import hashlib

try:
    from config.settings import KNOWLEDGE_BASE_DIR, KNOWLEDGE_BASE_CONFIG
    from shared.chromadb_service import get_chromadb_service
    from shared.sqlite_service import get_sqlite_service
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False

logger = logging.getLogger(__name__)

class KnowledgeBaseLoader:
    def __init__(self):
        if not CONFIG_AVAILABLE:
            raise ImportError("Configurações não disponíveis")
        
        self.kb_dir = Path(KNOWLEDGE_BASE_DIR)
        self.config = KNOWLEDGE_BASE_CONFIG
        self.chromadb = get_chromadb_service()
        self.sqlite = get_sqlite_service()
        
        self.kb_dir.mkdir(parents=True, exist_ok=True)
    
    def create_knowledge_base_documents(self) -> Dict[str, bool]:
        documents = {
            "ondasetrona_8mg_bula.txt": self._create_ondasetrona_bula(),
            "dexametasona_4mg_bula.txt": self._create_dexametasona_bula(),
            "metoclopramida_10mg_bula.txt": self._create_metoclopramida_bula(),
            "orientacoes_quimioterapia.txt": self._create_orientacoes_quimioterapia(),
            "guia_alimentacao_oncologica.txt": self._create_guia_alimentacao(),
            "sinais_alerta_emergencia.txt": self._create_sinais_alerta(),
            "cuidados_cateter_venoso.txt": self._create_cuidados_cateter(),
            "apoio_emocional_paciente.txt": self._create_apoio_emocional()
        }
        
        results = {}
        
        for filename, content in documents.items():
            try:
                file_path = self.kb_dir / filename
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                results[filename] = True
                logger.info(f"✅ Criado: {filename}")
            except Exception as e:
                results[filename] = False
                logger.error(f"❌ Erro {filename}: {e}")
        
        return results
    
    def load_documents_to_vector_store(self) -> Tuple[bool, str]:
        try:
            if not self.chromadb.is_available():
                return False, "ChromaDB não disponível"
            
            if not self.sqlite.is_available():
                return False, "SQLite não disponível"
            
            creation_results = self.create_knowledge_base_documents()
            
            loaded_count = 0
            total_chunks = 0
            
            for filename in self.config["required_documents"]:
                file_path = self.kb_dir / filename
                
                if not file_path.exists():
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if len(content.strip()) < 100:
                        continue
                    
                    metadata = {"filename": filename, "document_type": "medical"}
                    document_id = filename.replace('.txt', '')
                    
                    chromadb_success = self.chromadb.add_document(document_id, content, metadata)
                    
                    if chromadb_success:
                        content_hash = hashlib.md5(content.encode()).hexdigest()
                        word_count = len(content.split())
                        chunk_count = max(1, len(content) // 1000)
                        
                        sqlite_success = self.sqlite.store_document_metadata(
                            document_id, filename, content_hash, "medical", 
                            word_count, chunk_count, metadata
                        )
                        
                        if sqlite_success:
                            loaded_count += 1
                            total_chunks += chunk_count
                            logger.info(f"✅ Carregado: {filename}")
                
                except Exception as e:
                    logger.error(f"Erro processar {filename}: {e}")
                    continue
            
            if loaded_count > 0:
                message = f"✅ Base carregada: {loaded_count} documentos, {total_chunks} chunks"
                return True, message
            else:
                return False, "❌ Nenhum documento carregado"
                
        except Exception as e:
            return False, f"❌ Erro: {e}"
    
    def _create_ondasetrona_bula(self) -> str:
        return """ONDASETRONA 8mg - COMPRIMIDOS

COMPOSIÇÃO
Cada comprimido contém:
Cloridrato de ondasetrona equivalente a 8mg de ondasetrona

INDICAÇÕES
A ondasetrona é indicada para:
- Prevenção de náuseas e vômitos induzidos por quimioterapia
- Prevenção de náuseas e vômitos pós-operatórios

POSOLOGIA
Adultos - Quimioterapia:
- 8mg por via oral 30 minutos antes da quimioterapia
- Seguido de 8mg a cada 8 horas por até 5 dias
- Dose máxima diária: 32mg

EFEITOS ADVERSOS
Comuns (≥1/100 e <1/10):
- Dor de cabeça
- Constipação
- Sensação de calor

CONTRAINDICAÇÕES
- Hipersensibilidade à ondasetrona
- Uso concomitante com apomorfina

ARMAZENAMENTO
Conservar em temperatura ambiente (15-30°C)
Proteger da luz e umidade"""
    
    def _create_dexametasona_bula(self) -> str:
        return """DEXAMETASONA 4mg - COMPRIMIDOS

COMPOSIÇÃO
Cada comprimido contém:
Dexametasona 4mg

INDICAÇÕES
A dexametasona é indicada para:
- Prevenção de náuseas e vômitos induzidos por quimioterapia
- Processos inflamatórios
- Condições alérgicas graves

POSOLOGIA
Quimioterapia (antiemético):
- 4 a 20mg por via oral antes da quimioterapia
- Manutenção: 4 a 8mg por dia durante 2 a 3 dias

EFEITOS ADVERSOS
Comuns:
- Aumento do apetite e ganho de peso
- Elevação da glicemia
- Irritabilidade
- Insônia

CONTRAINDICAÇÕES
- Hipersensibilidade à dexametasona
- Infecções sistêmicas não controladas"""
    
    def _create_metoclopramida_bula(self) -> str:
        return """METOCLOPRAMIDA 10mg - COMPRIMIDOS

COMPOSIÇÃO
Cada comprimido contém:
Cloridrato de metoclopramida equivalente a 10mg de metoclopramida

INDICAÇÕES
A metoclopramida é indicada para:
- Náuseas e vômitos de origem central e periférica
- Distúrbios da motilidade gastroesofágica

POSOLOGIA
Adultos:
- 10mg, 3 a 4 vezes ao dia
- 30 minutos antes das refeições
- Dose máxima: 0,5mg/kg/dia
- Uso máximo: 5 dias consecutivos

EFEITOS ADVERSOS
Comuns:
- Sonolência
- Fadiga
- Agitação

CONTRAINDICAÇÕES
- Hipersensibilidade à metoclopramida
- Obstrução gastrintestinal
- Feocromocitoma"""
    
    def _create_orientacoes_quimioterapia(self) -> str:
        return """ORIENTAÇÕES PARA QUIMIOTERAPIA

PREPARAÇÃO ANTES DA SESSÃO

Preparação Alimentar:
- Faça uma refeição leve 2 horas antes do procedimento
- Evite alimentos gordurosos, muito condimentados ou ácidos
- Beba pelo menos 2 litros de água nas 24 horas anteriores
- Prefira frutas, verduras cozidas e carnes magras

Medicação Pré-Quimioterapia:
- Tome todos os medicamentos conforme prescrito
- Ondasetrona 8mg deve ser tomada 30 minutos antes da infusão
- Dexametasona conforme orientação médica
- Não atrase ou pule doses da pré-medicação

DURANTE A SESSÃO

Comunicação com a Equipe:
- Informe qualquer desconforto imediatamente
- Comunique dor, ardor ou inchaço no local da infusão
- Relate qualquer sintoma incomum

APÓS A SESSÃO

Primeiras 24-48 Horas:
- Continue tomando os medicamentos prescritos
- Beba bastante líquido: 2-3 litros de água por dia
- Descanse adequadamente
- Evite atividades físicas intensas
- Evite aglomerações por 48-72 horas

QUANDO PROCURAR AJUDA MÉDICA
- Febre acima de 37,8°C
- Vômitos persistentes
- Sangramento anormal
- Dificuldade respiratória"""
    
    def _create_guia_alimentacao(self) -> str:
        return """GUIA DE ALIMENTAÇÃO ONCOLÓGICA

ALIMENTOS RECOMENDADOS

Proteínas:
- Carnes magras bem cozidas
- Ovos bem cozidos
- Laticínios pasteurizados
- Leguminosas

Carboidratos:
- Arroz, macarrão, pães
- Batata, mandioca
- Aveia, quinoa

ALIMENTOS A EVITAR

Riscos de Infecção:
- Carnes cruas ou mal passadas
- Peixes crus (sushi, sashimi)
- Ovos crus
- Leite não pasteurizado

GERENCIAMENTO DE SINTOMAS

Para Náuseas:
- Faça refeições pequenas e frequentes
- Prefira alimentos secos pela manhã
- Chá de gengibre pode ajudar

Para Diarreia:
- Aumente ingestão de líquidos
- Evite alimentos ricos em fibras
- Prefira arroz, banana, maçã sem casca

HIDRATAÇÃO
- Beba pelo menos 2-3 litros de líquidos por dia
- Água é a melhor opção
- Monitore cor da urina"""
    
    def _create_sinais_alerta(self) -> str:
        return """PROTOCOLO - SINAIS DE ALERTA EM ONCOLOGIA

SINAIS DE EMERGÊNCIA ONCOLÓGICA

Febre e Infecção:
URGENTE - Procure imediatamente se:
- Febre ≥ 38°C
- Calafrios intensos
- Sinais de infecção (vermelhidão, pus)
- Dificuldade respiratória

Sangramento:
URGENTE - Procure imediatamente se:
- Sangramento digestivo
- Sangramento urinário intenso
- Sangramento nasal que não para
- Hematomas extensos

Problemas Respiratórios:
URGENTE - Procure imediatamente se:
- Falta de ar progressiva
- Dor no peito
- Tosse com sangue

SINAIS GASTROESOFÁGICOS

Náuseas e Vômitos:
ATENÇÃO - Procure se:
- Vômitos persistentes por mais de 24 horas
- Incapacidade de manter líquidos
- Vômito com sangue

CONTATOS DE EMERGÊNCIA
- Hospital: (11) 1234-5678
- Plantão oncológico: (11) 9876-5432
- SAMU: 192"""
    
    def _create_cuidados_cateter(self) -> str:
        return """CUIDADOS COM CATETER VENOSO CENTRAL

O QUE É O CATETER VENOSO CENTRAL
O cateter venoso central é um dispositivo colocado em uma veia grande para facilitar a administração de medicamentos durante o tratamento oncológico.

CUIDADOS DIÁRIOS

Higiene Geral:
- Lave sempre as mãos antes de tocar o cateter
- Use sabão antibacteriano ou álcool gel 70%
- Mantenha unhas curtas e limpas
- Evite tocar o cateter desnecessariamente

Proteção do Cateter:
- Mantenha o curativo sempre limpo e seco
- Proteja durante o banho com filme plástico
- Evite movimentos bruscos

BANHO E HIGIENE

Banho de Chuveiro:
- Proteja o cateter com filme plástico transparente
- Cole bem as bordas
- Tome banho rapidamente
- Remova a proteção cuidadosamente

SINAIS DE ALERTA

Infecção Local:
PROCURE IMEDIATAMENTE se apresentar:
- Vermelhidão ao redor do cateter
- Inchaço ou endurecimento local
- Dor ou sensibilidade aumentada
- Secreção purulenta
- Febre associada

EMERGÊNCIAS
- Sangramento persistente
- Ruptura ou dano ao cateter
- Dor intensa no local

CONTATOS IMPORTANTES
- Hospital: (11) 1234-5678
- Emergência: (11) 9876-5432"""
    
    def _create_apoio_emocional(self) -> str:
        return """GUIA DE APOIO EMOCIONAL

ENTENDENDO AS EMOÇÕES

Reações Normais ao Diagnóstico:
O diagnóstico de câncer pode gerar diversas emoções:
- Choque e negação inicial
- Medo e ansiedade sobre o futuro
- Raiva e questionamentos
- Tristeza e momentos de desespero
- Esperança e determinação

ESTRATÉGIAS DE ENFRENTAMENTO

Técnicas de Relaxamento:
- Respiração profunda
- Relaxamento muscular progressivo
- Meditação guiada
- Exercícios de mindfulness
- Prática de yoga adaptada

Atividades Terapêuticas:
- Escrever em um diário
- Pintar, desenhar ou artesanato
- Jardinagem
- Culinária
- Leitura de livros inspiradores

CONSTRUINDO REDE DE APOIO

Família e Amigos:
- Comunique suas necessidades claramente
- Aceite ajuda oferecida
- Mantenha relacionamentos importantes
- Estabeleça limites quando necessário

Grupos de Apoio:
- Participe de grupos de pacientes oncológicos
- Compartilhe experiências
- Aprenda com outros

LIDANDO COM MEDOS ESPECÍFICOS

Medo da Morte:
- Converse sobre seus medos abertamente
- Concentre-se no presente
- Faça planos para o futuro
- Busque significado e propósito

QUANDO BUSCAR AJUDA PROFISSIONAL
- Sintomas interferem nas atividades diárias
- Isolamento social prolongado
- Pensamentos de autolesão

RECURSOS DISPONÍVEIS
- Centro de Valorização da Vida: 188
- Psicólogo do hospital: (11) 2345-6789
- Grupos de apoio: (11) 4567-8901"""

def load_complete_knowledge_base() -> Tuple[bool, str]:
    try:
        loader = KnowledgeBaseLoader()
        return loader.load_documents_to_vector_store()
    except Exception as e:
        return False, f"Erro: {e}"

def validate_knowledge_base() -> Dict[str, Any]:
    try:
        chromadb = get_chromadb_service()
        
        if not chromadb.is_available():
            return {"valid": False, "error": "ChromaDB não disponível"}
        
        stats = chromadb.get_collection_stats()
        required_docs = len(KNOWLEDGE_BASE_CONFIG["required_documents"])
        actual_docs = stats.get("total_documents", 0)
        
        return {
            "valid": actual_docs >= required_docs,
            "required_documents": required_docs,
            "loaded_documents": actual_docs,
            "total_chunks": stats.get("total_chunks", 0),
            "friendly_names": stats.get("friendly_names", [])
        }
    except Exception as e:
        return {"valid": False, "error": str(e)}

def test_knowledge_base_loader() -> Dict[str, Any]:
    results = {
        "loader_creation": False,
        "documents_creation": False,
        "vector_store_loading": False,
        "validation": False,
        "errors": []
    }
    
    try:
        loader = KnowledgeBaseLoader()
        results["loader_creation"] = True
        
        creation_results = loader.create_knowledge_base_documents()
        success_count = sum(1 for success in creation_results.values() if success)
        results["documents_creation"] = success_count >= 6
        
        load_success, load_message = loader.load_documents_to_vector_store()
        results["vector_store_loading"] = load_success
        
        if not load_success:
            results["errors"].append(f"Falha carregamento: {load_message}")
        
        validation = validate_knowledge_base()
        results["validation"] = validation.get("valid", False)
        
        if not validation.get("valid"):
            results["errors"].append(f"Validação falhou: {validation.get('error', 'Desconhecido')}")
        
    except Exception as e:
        results["errors"].append(f"Erro geral: {e}")
    
    return results
