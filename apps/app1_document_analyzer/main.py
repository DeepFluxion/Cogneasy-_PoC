"""
App 1: Document Analyzer - FASE 2C Integrado (SINTAXE CORRIGIDA)
Análise de documentos médicos com infraestrutura real
CORREÇÃO FINAL: Corrigido erro de sintaxe na linha 725
"""

import streamlit as st
from pathlib import Path
import sys
import json
from datetime import datetime
import time
import logging

# Adicionar pasta raiz ao path
root_path = Path(__file__).parent.parent.parent
sys.path.append(str(root_path))

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importar serviços da infraestrutura FASE 2C
try:
    from shared.openai_service_real import get_openai_service
    from shared.chromadb_service import get_chromadb_service
    from shared.sqlite_service import get_sqlite_service
    SERVICES_AVAILABLE = True
    logger.info("✅ Serviços FASE 2C carregados com sucesso")
except ImportError as e:
    SERVICES_AVAILABLE = False
    logger.warning(f"⚠️ Serviços FASE 2C não disponíveis: {e}")

def run_document_analyzer():
    """Função principal do Document Analyzer - FASE 2C INTEGRADO"""
    
    st.title("📄 Document Analyzer - FASE 2C")
    st.markdown("### Análise Inteligente com IA Real")
    
    # Status da infraestrutura
    show_infrastructure_status()
    
    # Inicializar session state específico do app
    if 'app1_documents' not in st.session_state:
        st.session_state.app1_documents = []
    
    if 'app1_extractions' not in st.session_state:
        st.session_state.app1_extractions = {}
    
    # Tabs para organizar funcionalidades
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📂 Upload", "🔍 Análise IA", "💬 Chat Real", "🔗 Integração", "📊 Histórico"])
    
    with tab1:
        show_upload_section()
    
    with tab2:
        show_ai_analysis_section()
    
    with tab3:
        show_real_chat_section()
    
    with tab4:
        show_integration_section()
    
    with tab5:
        show_history_section()

def show_infrastructure_status():
    """Mostra status da infraestrutura FASE 2C"""
    
    with st.expander("🔧 Status da Infraestrutura FASE 2C", expanded=False):
        
        if not SERVICES_AVAILABLE:
            st.error("❌ Serviços FASE 2C não disponíveis - funcionando em modo simulado")
            return
        
        col1, col2, col3 = st.columns(3)
        
        try:
            openai_service = get_openai_service()
            chromadb_service = get_chromadb_service()
            sqlite_service = get_sqlite_service()
            
            with col1:
                if openai_service.is_available():
                    st.success("✅ OpenAI Conectada")
                else:
                    st.error("❌ OpenAI Indisponível")
            
            with col2:
                if chromadb_service.is_available():
                    st.success("✅ ChromaDB Ativo")
                else:
                    st.error("❌ ChromaDB Indisponível")
            
            with col3:
                if sqlite_service.is_available():
                    st.success("✅ SQLite Operacional")
                else:
                    st.error("❌ SQLite Indisponível")
                    
        except Exception as e:
            st.error(f"❌ Erro ao verificar serviços: {e}")

def show_upload_section():
    """Seção de upload de documentos"""
    
    st.markdown("#### 📂 Upload de Documentos")
    
    # File uploader
    uploaded_files = st.file_uploader(
        "Selecione documentos médicos",
        type=['pdf', 'jpg', 'jpeg', 'png', 'txt'],
        accept_multiple_files=True,
        help="Aceita: receitas, exames, relatórios médicos"
    )
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} arquivo(s) carregado(s)")
        
        # Mostrar arquivos carregados
        for i, file in enumerate(uploaded_files):
            with st.expander(f"📄 {file.name} ({file.size} bytes)"):
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.info(f"**Tipo:** {file.type}")
                    st.info(f"**Tamanho:** {file.size} bytes")
                
                with col2:
                    # Botão para processar arquivo
                    if st.button(f"🔬 Processar com IA", key=f"process_{i}"):
                        process_document_with_ai(file)

def process_document_with_ai(uploaded_file):
    """Processa documento usando IA real da FASE 2C"""
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Etapa 1: Ler arquivo
        status_text.text("📖 Lendo arquivo...")
        progress_bar.progress(20)
        
        # Simular leitura do arquivo
        file_content = uploaded_file.read()
        if isinstance(file_content, bytes):
            try:
                file_content = file_content.decode('utf-8')
            except:
                file_content = f"Arquivo binário: {uploaded_file.name}"
        
        # Etapa 2: Análise com OpenAI
        status_text.text("🤖 Analisando com OpenAI...")
        progress_bar.progress(50)
        
        extraction = analyze_document_with_openai(uploaded_file.name, file_content)
        
        # Etapa 3: Salvar no ChromaDB
        status_text.text("💾 Salvando no ChromaDB...")
        progress_bar.progress(70)
        
        save_document_to_chromadb(uploaded_file.name, file_content, extraction)
        
        # Etapa 4: Registrar no SQLite
        status_text.text("📊 Registrando metadados...")
        progress_bar.progress(90)
        
        save_document_to_sqlite(uploaded_file.name, extraction)
        
        # Etapa 5: Salvar localmente
        status_text.text("💽 Finalizando...")
        progress_bar.progress(100)
        
        # Adicionar ao session state
        doc_data = {
            'id': f"doc_{len(st.session_state.app1_documents)}_{int(time.time())}",
            'filename': uploaded_file.name,
            'type': uploaded_file.type,
            'size': uploaded_file.size,
            'upload_time': datetime.now(),
            'extraction': extraction,
            'processed_with_ai': True
        }
        
        st.session_state.app1_documents.append(doc_data)
        st.session_state.app1_extractions[doc_data['id']] = extraction
        
        status_text.text("✅ Processamento concluído!")
        
        # Mostrar resultado
        st.success(f"🎉 Documento '{uploaded_file.name}' processado com IA!")
        
        # Preview da análise
        with st.expander("👁️ Preview da Análise", expanded=True):
            show_extraction_preview(extraction)
            
        # Botão para integração automática
        if st.button("🔗 Integrar com App 3", key=f"integrate_{doc_data['id']}"):
            integrate_document_with_app3(doc_data)
        
    except Exception as e:
        progress_bar.progress(0)
        status_text.text("❌ Erro no processamento")
        st.error(f"Erro: {e}")
        logger.error(f"Erro ao processar documento: {e}")
        
        # Fallback para simulação
        st.warning("🔄 Usando simulação como fallback...")
        extraction = create_simulated_extraction(uploaded_file.name)
        
        doc_data = {
            'id': f"doc_{len(st.session_state.app1_documents)}_{int(time.time())}",
            'filename': uploaded_file.name,
            'type': uploaded_file.type,
            'size': uploaded_file.size,
            'upload_time': datetime.now(),
            'extraction': extraction,
            'processed_with_ai': False
        }
        
        st.session_state.app1_documents.append(doc_data)

def analyze_document_with_openai(filename, content):
    """Analisa documento usando OpenAI real - FUNÇÃO RENOMEADA PARA EVITAR RECURSÃO"""
    
    if not SERVICES_AVAILABLE:
        return create_simulated_extraction(filename)
    
    try:
        openai_service = get_openai_service()
        
        # Determinar tipo de documento baseado no nome
        doc_type = classify_document_type(filename)
        
        # Prompt específico para análise médica
        prompt = f"""
        Analise este documento médico: {filename}
        
        Conteúdo:
        {content[:2000]}
        
        Extraia as seguintes informações em formato JSON:
        {{
            "tipo_documento": "{doc_type}",
            "arquivo": "{filename}",
            "data_processamento": "{datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "informacoes_principais": ["lista", "de", "informações"],
            "medicamentos": [
                {{"nome": "medicamento", "dosagem": "dose", "frequencia": "freq"}}
            ],
            "orientacoes": ["orientação1", "orientação2"],
            "eventos_sugeridos": [
                {{"tipo": "tipo", "titulo": "titulo", "data": "data"}}
            ],
            "todo_list": ["tarefa1", "tarefa2"],
            "confianca": 0.9
        }}
        
        Foque em informações médicas relevantes para pacientes oncológicos.
        """
        
        # Fazer chamada para OpenAI
        response = openai_service.generate_text(
            prompt=prompt,
            max_tokens=1000,
            temperature=0.1
        )
        
        # Tentar parsear resposta como JSON
        try:
            extraction = json.loads(response)
            extraction['ai_processed'] = True
            extraction['ai_confidence'] = extraction.get('confianca', 0.8)
            return extraction
        except json.JSONDecodeError:
            # Se não conseguir parsear, criar estrutura básica
            return {
                'tipo_documento': doc_type,
                'arquivo': filename,
                'data_processamento': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'ai_response': response,
                'ai_processed': True,
                'ai_confidence': 0.7,
                'informacoes_principais': ["Documento analisado por IA"],
                'eventos_sugeridos': [],
                'todo_list': ["Revisar análise da IA"]
            }
        
    except Exception as e:
        logger.error(f"Erro na análise OpenAI: {e}")
        extraction = create_simulated_extraction(filename)
        extraction['ai_error'] = str(e)
        return extraction

def save_document_to_chromadb(filename, content, extraction):
    """Salva documento no ChromaDB - FUNÇÃO RENOMEADA PARA EVITAR RECURSÃO"""
    
    if not SERVICES_AVAILABLE:
        return
    
    try:
        chromadb_service = get_chromadb_service()
        
        # Preparar metadados
        metadata = {
            'filename': filename,
            'document_type': extraction.get('tipo_documento', 'unknown'),
            'processed_date': datetime.now().isoformat(),
            'app': 'app1_document_analyzer'
        }
        
        # Adicionar documento ao ChromaDB
        doc_id = f"app1_{filename}_{int(time.time())}"
        
        chromadb_service.add_document(
            doc_id=doc_id,
            content=content,
            metadata=metadata
        )
        
        logger.info(f"✅ Documento salvo no ChromaDB: {doc_id}")
        
    except Exception as e:
        logger.error(f"Erro ao salvar no ChromaDB: {e}")

def save_document_to_sqlite(filename, extraction):
    """Salva metadados no SQLite - FUNÇÃO RENOMEADA PARA EVITAR RECURSÃO"""
    
    if not SERVICES_AVAILABLE:
        return
    
    try:
        sqlite_service = get_sqlite_service()
        
        # Preparar dados para SQLite
        document_data = {
            'filename': filename,
            'document_type': extraction.get('tipo_documento', 'unknown'),
            'metadata_json': json.dumps(extraction),
            'app_source': 'app1_document_analyzer',
            'ai_processed': extraction.get('ai_processed', False),
            'confidence_score': extraction.get('ai_confidence', 0.0)
        }
        
        # Salvar no SQLite
        sqlite_service.save_document_metadata(document_data)
        
        logger.info(f"✅ Metadados salvos no SQLite: {filename}")
        
    except Exception as e:
        logger.error(f"Erro ao salvar no SQLite: {e}")

def classify_document_type(filename):
    """Classifica tipo de documento baseado no nome do arquivo"""
    
    filename_lower = filename.lower()
    
    if any(word in filename_lower for word in ['receita', 'prescription', 'rx']):
        return 'receita_medica'
    elif any(word in filename_lower for word in ['exame', 'lab', 'test', 'resultado']):
        return 'exame_laboratorial'
    elif any(word in filename_lower for word in ['relatorio', 'report', 'consulta']):
        return 'relatorio_medico'
    elif any(word in filename_lower for word in ['bula', 'medication', 'drug']):
        return 'bula_medicamento'
    else:
        return 'documento_generico'

def create_simulated_extraction(filename):
    """Cria extração simulada para fallback"""
    
    doc_type = classify_document_type(filename)
    
    if doc_type == 'receita_medica':
        return {
            'tipo_documento': 'receita_medica',
            'arquivo': filename,
            'data_processamento': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'medico': 'Dr. Exemplo Santos',
            'especialidade': 'Oncologia',
            'paciente': 'Paciente Exemplo',
            'medicamentos': [
                {
                    'nome': 'Ondasetrona',
                    'dosagem': '8mg',
                    'frequencia': '8/8h',
                    'via': 'oral',
                    'duracao': '5 dias'
                },
                {
                    'nome': 'Dexametasona',
                    'dosagem': '4mg',
                    'frequencia': '12/12h',
                    'via': 'oral',
                    'duracao': '3 dias'
                }
            ],
            'eventos_sugeridos': [
                {
                    'tipo': 'medicamento',
                    'titulo': 'Ondasetrona 8mg',
                    'data': datetime.now().strftime('%Y-%m-%d')
                }
            ],
            'todo_list': [
                'Tomar medicamentos conforme prescrição',
                'Anotar efeitos colaterais',
                'Retornar em caso de piora'
            ],
            'ai_processed': False,
            'ai_confidence': 0.5
        }
    else:
        return {
            'tipo_documento': doc_type,
            'arquivo': filename,
            'data_processamento': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'informacoes_principais': ['Documento médico processado'],
            'eventos_sugeridos': [],
            'todo_list': ['Revisar documento com equipe médica'],
            'ai_processed': False,
            'ai_confidence': 0.5
        }

def show_extraction_preview(extraction):
    """Mostra preview da extração"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"**Tipo:** {extraction.get('tipo_documento', 'N/A')}")
        st.info(f"**Processado:** {extraction.get('data_processamento', 'N/A')}")
        
        if extraction.get('ai_processed'):
            st.success(f"✅ IA Real (Confiança: {extraction.get('ai_confidence', 0)*100:.0f}%)")
        else:
            st.warning("⚠️ Simulação")
    
    with col2:
        if 'medicamentos' in extraction:
            st.write(f"**Medicamentos:** {len(extraction['medicamentos'])}")
        if 'eventos_sugeridos' in extraction:
            st.write(f"**Eventos:** {len(extraction['eventos_sugeridos'])}")
        if 'todo_list' in extraction:
            st.write(f"**Tarefas:** {len(extraction['todo_list'])}")

def show_ai_analysis_section():
    """Seção de análise com IA"""
    
    st.markdown("#### 🔍 Análise com IA Real")
    
    if not st.session_state.app1_documents:
        st.info("📋 Nenhum documento foi processado ainda. Use a aba 'Upload' para começar.")
        return
    
    # Seletor de documento
    doc_options = [f"{doc['filename']} ({doc['upload_time'].strftime('%d/%m %H:%M')})" 
                   for doc in st.session_state.app1_documents]
    
    selected_idx = st.selectbox("📄 Selecione um documento:", range(len(doc_options)), 
                               format_func=lambda x: doc_options[x])
    
    if selected_idx is not None:
        doc = st.session_state.app1_documents[selected_idx]
        extraction = doc['extraction']
        
        # Mostrar análise completa
        show_complete_analysis(extraction)

def show_complete_analysis(extraction):
    """Mostra análise completa do documento"""
    
    # Informações básicas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📄 Tipo", extraction.get('tipo_documento', 'N/A').replace('_', ' ').title())
    
    with col2:
        if extraction.get('ai_processed'):
            st.metric("🤖 IA", "Real", delta="Ativo")
        else:
            st.metric("🤖 IA", "Simulação", delta="Inativo")
    
    with col3:
        confidence = extraction.get('ai_confidence', 0.5)
        st.metric("📊 Confiança", f"{confidence*100:.0f}%")
    
    # Medicamentos (se existir)
    if 'medicamentos' in extraction and extraction['medicamentos']:
        st.markdown("#### 💊 Medicamentos Identificados")
        
        for med in extraction['medicamentos']:
            with st.expander(f"💊 {med.get('nome', 'Medicamento')}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Dosagem:** {med.get('dosagem', 'N/A')}")
                    st.write(f"**Frequência:** {med.get('frequencia', 'N/A')}")
                
                with col2:
                    st.write(f"**Via:** {med.get('via', 'N/A')}")
                    st.write(f"**Duração:** {med.get('duracao', 'N/A')}")
    
    # Eventos sugeridos
    if 'eventos_sugeridos' in extraction and extraction['eventos_sugeridos']:
        st.markdown("#### 📅 Eventos Sugeridos")
        
        for evento in extraction['eventos_sugeridos']:
            st.info(f"📅 {evento.get('titulo', 'Evento')} - {evento.get('data', 'Data não definida')}")
    
    # Todo list
    if 'todo_list' in extraction and extraction['todo_list']:
        st.markdown("#### ✅ Lista de Tarefas")
        
        for task in extraction['todo_list']:
            st.write(f"• {task}")

def show_real_chat_section():
    """Seção de chat real com IA"""
    
    st.markdown("#### 💬 Chat com IA Real")
    
    if not st.session_state.app1_documents:
        st.info("📋 Processe alguns documentos primeiro para usar o chat com IA.")
        return
    
    # Inicializar histórico de chat
    if 'app1_chat_history' not in st.session_state:
        st.session_state.app1_chat_history = []
    
    # Mostrar histórico de chat
    chat_container = st.container()
    
    with chat_container:
        for i, message in enumerate(st.session_state.app1_chat_history[-10:]):  # Últimas 10 mensagens
            if message['role'] == 'user':
                st.chat_message("user").write(message['content'])
            else:
                st.chat_message("assistant").write(message['content'])
    
    # Input do usuário
    user_question = st.chat_input("Faça uma pergunta sobre seus documentos...")
    
    if user_question:
        # Adicionar mensagem do usuário
        st.session_state.app1_chat_history.append({
            'role': 'user',
            'content': user_question,
            'timestamp': datetime.now()
        })
        
        # Gerar resposta com IA
        response = generate_ai_chat_response(user_question)
        
        # Adicionar resposta da IA
        st.session_state.app1_chat_history.append({
            'role': 'assistant',
            'content': response,
            'timestamp': datetime.now()
        })
        
        st.rerun()

def generate_ai_chat_response(question):
    """Gera resposta usando IA real"""
    
    if not SERVICES_AVAILABLE:
        return generate_simulated_response(question)
    
    try:
        openai_service = get_openai_service()
        
        # Preparar contexto dos documentos
        context = "Documentos do usuário:\n"
        for doc in st.session_state.app1_documents:
            extraction = doc['extraction']
            context += f"\n- {doc['filename']}: {extraction.get('tipo_documento', 'N/A')}"
            if 'medicamentos' in extraction:
                context += f" (Medicamentos: {[med['nome'] for med in extraction['medicamentos']]})"
        
        # Prompt para o chat
        prompt = f"""
        Você é um assistente médico especializado em oncologia.
        
        Contexto dos documentos do usuário:
        {context}
        
        Pergunta do usuário: {question}
        
        Responda de forma clara, precisa e útil, baseando-se nos documentos processados.
        Se a pergunta não puder ser respondida com base nos documentos, informe isso claramente.
        """
        
        response = openai_service.generate_text(
            prompt=prompt,
            max_tokens=500,
            temperature=0.3
        )
        
        return f"🤖 {response}\n\n*Resposta gerada por IA real baseada em seus documentos*"
        
    except Exception as e:
        logger.error(f"Erro na geração de resposta: {e}")
        return f"❌ Erro na IA: {e}\n\nUsando resposta simulada:\n{generate_simulated_response(question)}"

def generate_simulated_response(question):
    """Gera resposta simulada para fallback"""
    
    question_lower = question.lower()
    
    if any(word in question_lower for word in ['medicamento', 'remedio', 'drug']):
        return "💊 Com base em seus documentos, identifiquei medicamentos para tratamento oncológico. Sempre siga as orientações médicas para dosagem e horários."
    
    elif any(word in question_lower for word in ['quando', 'horario', 'schedule']):
        return "⏰ Para informações sobre horários de medicação, verifique as prescrições processadas. Recomendo criar lembretes para não esquecer."
    
    elif any(word in question_lower for word in ['efeito', 'colateral', 'side']):
        return "⚠️ Efeitos colaterais são importantes de monitorar. Anote qualquer sintoma e comunique à equipe médica."
    
    else:
        return f"🤔 Pergunta interessante sobre: '{question}'. Com base nos documentos processados, posso ajudar com informações sobre medicamentos, horários e orientações médicas."

def show_integration_section():
    """Seção de integração com outros apps"""
    
    st.markdown("#### 🔗 Integração FASE 2C")
    
    if not st.session_state.app1_documents:
        st.info("📋 Processe alguns documentos primeiro para usar a integração.")
        return
    
    st.markdown("##### 📤 Integração com App 3 (Document Chat)")
    
    # Seletor de documento para integração
    doc_options = [f"{doc['filename']}" for doc in st.session_state.app1_documents]
    
    if doc_options:
        selected_doc = st.selectbox("📄 Documento para integrar:", doc_options)
        
        if selected_doc:
            # Encontrar documento selecionado
            doc_data = next((doc for doc in st.session_state.app1_documents 
                           if doc['filename'] == selected_doc), None)
            
            if doc_data:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.info(f"**Arquivo:** {doc_data['filename']}")
                    st.info(f"**Tipo:** {doc_data['extraction'].get('tipo_documento', 'N/A')}")
                
                with col2:
                    if doc_data['extraction'].get('ai_processed'):
                        st.success("✅ Processado com IA Real")
                    else:
                        st.warning("⚠️ Simulação")
                
                # Botão de integração
                if st.button("🚀 Integrar com App 3", key="integrate_app3"):
                    integrate_document_with_app3(doc_data)

def integrate_document_with_app3(doc_data):
    """Integra documento com App 3 - FUNÇÃO RENOMEADA PARA EVITAR RECURSÃO"""
    
    try:
        # Preparar dados para integração
        integration_data = {
            'source': 'app1_document_analyzer',
            'document_id': doc_data['id'],
            'filename': doc_data['filename'],
            'extraction': doc_data['extraction'],
            'timestamp': datetime.now().isoformat()
        }
        
        # Salvar dados de integração no session state
        if 'app3_integrated_docs' not in st.session_state:
            st.session_state.app3_integrated_docs = []
        
        st.session_state.app3_integrated_docs.append(integration_data)
        
        # Marcar documento como integrado
        doc_data['integrated_app3'] = True
        doc_data['integration_timestamp'] = datetime.now()
        
        # Se possível, adicionar ao ChromaDB com tag de integração
        if SERVICES_AVAILABLE:
            try:
                chromadb_service = get_chromadb_service()
                
                # Adicionar documento com metadata de integração
                doc_content = f"Documento integrado do App 1: {doc_data['filename']}\n"
                doc_content += f"Tipo: {doc_data['extraction'].get('tipo_documento', 'N/A')}\n"
                
                if 'medicamentos' in doc_data['extraction']:
                    doc_content += "\nMedicamentos:\n"
                    for med in doc_data['extraction']['medicamentos']:
                        doc_content += f"- {med.get('nome', 'N/A')}: {med.get('dosagem', 'N/A')}\n"
                
                metadata = {
                    'source_app': 'app1_document_analyzer',
                    'document_type': doc_data['extraction'].get('tipo_documento', 'unknown'),
                    'integrated': True,
                    'integration_date': datetime.now().isoformat(),
                    'filename': doc_data['filename']
                }
                
                integration_doc_id = f"app1_integrated_{doc_data['id']}"
                
                chromadb_service.add_document(
                    doc_id=integration_doc_id,
                    content=doc_content,
                    metadata=metadata
                )
                
                logger.info(f"✅ Documento integrado no ChromaDB: {integration_doc_id}")
                
            except Exception as e:
                logger.error(f"Erro na integração ChromaDB: {e}")
        
        st.success(f"🎉 Documento '{doc_data['filename']}' integrado com App 3!")
        st.info("💡 Agora você pode fazer perguntas sobre este documento no App 3")
        
    except Exception as e:
        st.error(f"❌ Erro na integração: {e}")
        logger.error(f"Erro ao integrar documento: {e}")

def show_history_section():
    """Seção de histórico de documentos"""
    
    st.markdown("#### 📊 Histórico de Documentos")
    
    if not st.session_state.app1_documents:
        st.info("📋 Nenhum documento foi processado ainda.")
        return
    
    # Métricas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📄 Total Docs", len(st.session_state.app1_documents))
    
    with col2:
        ai_count = len([doc for doc in st.session_state.app1_documents 
                       if doc['extraction'].get('ai_processed', False)])
        st.metric("🤖 IA Real", ai_count)
    
    with col3:
        integrated_count = len([doc for doc in st.session_state.app1_documents 
                              if doc.get('integrated_app3', False)])
        st.metric("🔗 Integrados", integrated_count)
    
    with col4:
        prescription_count = len([doc for doc in st.session_state.app1_documents 
                                if doc['extraction']['tipo_documento'] == 'receita_medica'])
        st.metric("💊 Receitas", prescription_count)
    
    # Lista de documentos
    st.markdown("#### 📋 Lista de Documentos")
    
    for i, doc in enumerate(st.session_state.app1_documents):
        with st.expander(f"📄 {doc['filename']} - {doc['upload_time'].strftime('%d/%m/%Y %H:%M')}"):
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write(f"**Tipo:** {doc['extraction']['tipo_documento'].replace('_', ' ').title()}")
                st.write(f"**Tamanho:** {doc['size']} bytes")
                
                if doc['extraction'].get('ai_processed'):
                    confidence = doc['extraction'].get('ai_confidence', 0.5)
                    st.success(f"🤖 IA Real ({confidence*100:.0f}%)")
                else:
                    st.warning("⚠️ Simulação")
            
            with col2:
                st.write(f"**ID:** {doc['id']}")
                st.write(f"**Formato:** {doc['type']}")
                
                if doc.get('integrated_app3'):
                    st.success("🔗 Integrado App 3")
                else:
                    st.info("📋 Não integrado")
            
            with col3:
                # Medicamentos (se houver)
                if 'medicamentos' in doc['extraction']:
                    med_count = len(doc['extraction']['medicamentos'])
                    st.write(f"**Medicamentos:** {med_count}")
                    
                    if med_count > 0:
                        med_names = [med['nome'] for med in doc['extraction']['medicamentos']]
                        st.write(f"**Lista:** {', '.join(med_names[:3])}{'...' if len(med_names) > 3 else ''}")
            
            # Ações
            st.markdown("**Ações:**")
            action_col1, action_col2, action_col3 = st.columns(3)
            
            with action_col1:
                if st.button(f"🔍 Ver Análise", key=f"view_{i}"):
                    st.session_state.selected_doc_for_analysis = i
                    st.rerun()
            
            with action_col2:
                if not doc.get('integrated_app3', False):
                    if st.button(f"🔗 Integrar App 3", key=f"integrate_{i}"):
                        integrate_document_with_app3(doc)
                        st.rerun()
                else:
                    st.success("✅ Integrado")
            
            with action_col3:
                if st.button(f"🗑️ Remover", key=f"remove_{i}"):
                    st.session_state.app1_documents.pop(i)
                    st.rerun()
            
            # Exportar dados
            export_data = {
                'documento': doc['filename'],
                'processado_em': doc['upload_time'].isoformat(),
                'extracao': doc['extraction'],
                'integrado_app3': doc.get('integrated_app3', False)
            }
            
            st.download_button(
                label="📥 Exportar JSON",
                data=json.dumps(export_data, indent=2, ensure_ascii=False),
                file_name=f"{doc['filename']}_analysis.json",
                mime="application/json",
                key=f"download_{i}"
            )

def main():
    """Função principal para compatibilidade"""
    run_document_analyzer()

if __name__ == "__main__":
    run_document_analyzer()