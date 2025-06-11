"""
App 2: Smart Scheduler - FASE 2C Integrado (CORRIGIDO)
Agenda inteligente com IA real e integração completa
CORREÇÃO: Removidas funções duplicadas que causavam recursão
"""

import streamlit as st
from pathlib import Path
import sys
import json
from datetime import datetime, date, timedelta
import time
import re
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

def run_smart_scheduler():
    """Função principal do Smart Scheduler - FASE 2C INTEGRADO"""
    
    st.title("📅 Smart Scheduler - FASE 2C")
    st.markdown("### Agenda Inteligente com IA Real")
    
    # Status da infraestrutura
    show_infrastructure_status()
    
    # Verificar integração com App 1
    check_app1_integration()
    
    # Inicializar session state específico do app
    if 'app2_events' not in st.session_state:
        st.session_state.app2_events = []
    
    if 'app2_calendar_view' not in st.session_state:
        st.session_state.app2_calendar_view = 'week'
    
    # Tabs para organizar funcionalidades
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["➕ Criar com IA", "📅 Visualizar", "💬 Chat Agenda", "🔗 Integração", "📊 Histórico"])
    
    with tab1:
        show_ai_create_section()
    
    with tab2:
        show_calendar_view_section()
    
    with tab3:
        show_ai_chat_section()
    
    with tab4:
        show_integration_section()
    
    with tab5:
        show_events_history_section()

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

def show_ai_create_section():
    """Seção para criar eventos usando IA real"""
    
    st.markdown("#### ➕ Criar Eventos com IA Real")
    
    # Exemplos de linguagem natural
    with st.expander("💡 Exemplos de linguagem natural"):
        st.markdown("""
        **Consultas:**
        • "Consulta com Dr. Silva na quinta-feira às 14h"
        • "Retorno oncologia dia 15 de fevereiro"
        
        **Medicamentos:**
        • "Tomar ondasetrona de 8 em 8 horas por 5 dias"
        • "Dexametasona 4mg pela manhã durante 3 dias"
        
        **Exames:**
        • "Hemograma no laboratório na segunda de manhã"
        • "TC de tórax no dia 20 às 10h"
        """)
    
    # Input principal
    user_input = st.text_area(
        "Descreva seu compromisso:",
        placeholder="Ex: Consulta com Dr. Ana amanhã às 15h para revisar exames",
        height=100
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🤖 Processar com IA Real", type="primary"):
            if user_input.strip():
                process_with_ai(user_input)
            else:
                st.warning("Digite um texto para processar")
    
    with col2:
        if st.button("⚡ Processamento Rápido"):
            if user_input.strip():
                process_with_simulation(user_input)
            else:
                st.warning("Digite um texto para processar")

def process_with_ai(user_input):
    """Processa entrada usando IA real"""
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Etapa 1: Análise com OpenAI
        status_text.text("🤖 Analisando com OpenAI...")
        progress_bar.progress(30)
        
        event_data = analyze_natural_language_with_openai(user_input)
        
        # Etapa 2: Salvar no ChromaDB
        status_text.text("💾 Salvando no ChromaDB...")
        progress_bar.progress(60)
        
        save_schedule_to_chromadb(user_input, event_data)
        
        # Etapa 3: Registrar no SQLite
        status_text.text("📊 Registrando metadados...")
        progress_bar.progress(80)
        
        save_schedule_to_sqlite(event_data)
        
        # Etapa 4: Criar eventos
        status_text.text("📅 Criando eventos...")
        progress_bar.progress(100)
        
        events_created = create_events_from_analysis(event_data, user_input)
        
        status_text.text("✅ Processamento concluído!")
        
        if events_created:
            st.success(f"🎉 {len(events_created)} evento(s) criado(s) com IA!")
            
            # Mostrar eventos criados
            with st.expander("👁️ Eventos Criados", expanded=True):
                for event in events_created:
                    show_event_preview(event)
        else:
            st.warning("Nenhum evento foi identificado no texto")
        
    except Exception as e:
        progress_bar.progress(0)
        status_text.text("❌ Erro no processamento com IA")
        st.error(f"Erro: {e}")
        logger.error(f"Erro ao processar com IA: {e}")
        
        # Fallback para simulação
        st.warning("🔄 Usando processamento rápido como fallback...")
        process_with_simulation(user_input)

def analyze_natural_language_with_openai(text):
    """Analisa texto usando OpenAI real"""
    
    if not SERVICES_AVAILABLE:
        return analyze_text_simulation(text)
    
    try:
        openai_service = get_openai_service()
        
        # Prompt específico para análise de eventos médicos
        prompt = f"""
        Analise este texto e extraia informações de eventos médicos em formato JSON:
        
        Texto: "{text}"
        
        Extraia as seguintes informações:
        {{
            "eventos": [
                {{
                    "tipo": "consulta|medicamento|exame|tratamento|outro",
                    "titulo": "título do evento",
                    "data": "YYYY-MM-DD ou 'hoje'|'amanha'|'segunda'|etc",
                    "horario": "HH:MM",
                    "descricao": "descrição detalhada",
                    "profissional": "nome do médico/profissional",
                    "local": "local do evento",
                    "prioridade": "alta|media|baixa",
                    "duracao": "duração em minutos",
                    "observacoes": "observações adicionais"
                }}
            ],
            "medicamentos": [
                {{
                    "nome": "nome do medicamento",
                    "dosagem": "dosagem",
                    "frequencia": "frequência (ex: 8/8h)",
                    "duracao": "duração do tratamento",
                    "horarios": ["08:00", "16:00", "00:00"]
                }}
            ],
            "confianca": 0.9,
            "categoria_principal": "tipo principal identificado"
        }}
        
        Foque em informações médicas para pacientes oncológicos.
        Se mencionar intervalos (8/8h, 12/12h), calcule os horários específicos.
        Para datas relativas (amanhã, segunda), mantenha o texto original.
        """
        
        # Fazer chamada para OpenAI
        response = openai_service.generate_text(
            prompt=prompt,
            max_tokens=1500,
            temperature=0.1
        )
        
        # Tentar parsear resposta como JSON
        try:
            ai_data = json.loads(response)
            ai_data['ai_processed'] = True
            ai_data['original_text'] = text
            ai_data['processed_at'] = datetime.now().isoformat()
            return ai_data
        except json.JSONDecodeError:
            # Se não conseguir parsear, criar estrutura básica
            return {
                'eventos': [],
                'medicamentos': [],
                'ai_processed': True,
                'ai_response': response,
                'confianca': 0.5,
                'categoria_principal': 'outro',
                'original_text': text,
                'processed_at': datetime.now().isoformat()
            }
        
    except Exception as e:
        logger.error(f"Erro na análise OpenAI: {e}")
        return analyze_text_simulation(text)

def analyze_text_simulation(text):
    """Análise simulada para fallback"""
    
    # Detectar tipos de eventos
    text_lower = text.lower()
    
    events = []
    medications = []
    
    # Detectar consultas
    if any(word in text_lower for word in ['consulta', 'dr.', 'dra.', 'médico', 'doutor']):
        events.append({
            'tipo': 'consulta',
            'titulo': 'Consulta médica',
            'data': extract_date_from_text(text),
            'horario': extract_time_from_text(text),
            'descricao': text,
            'prioridade': 'alta',
            'duracao': 60
        })
    
    # Detectar medicamentos
    medication_patterns = ['ondasetrona', 'dexametasona', 'metoclopramida', 'paracetamol']
    for med in medication_patterns:
        if med in text_lower:
            medications.append({
                'nome': med.title(),
                'dosagem': extract_dosage_from_text(text, med),
                'frequencia': extract_frequency_from_text(text),
                'horarios': generate_medication_schedule(text)
            })
    
    # Detectar exames
    if any(word in text_lower for word in ['exame', 'tc', 'rm', 'hemograma', 'laboratório']):
        events.append({
            'tipo': 'exame',
            'titulo': 'Exame médico',
            'data': extract_date_from_text(text),
            'horario': extract_time_from_text(text),
            'descricao': text,
            'prioridade': 'media',
            'duracao': 30
        })
    
    return {
        'eventos': events,
        'medicamentos': medications,
        'ai_processed': False,
        'confianca': 0.6,
        'categoria_principal': events[0]['tipo'] if events else 'outro',
        'original_text': text,
        'processed_at': datetime.now().isoformat()
    }

def extract_date_from_text(text):
    """Extrai data do texto"""
    
    text_lower = text.lower()
    today = date.today()
    
    if 'hoje' in text_lower:
        return today.strftime('%Y-%m-%d')
    elif 'amanha' in text_lower or 'amanhã' in text_lower:
        return (today + timedelta(days=1)).strftime('%Y-%m-%d')
    elif 'segunda' in text_lower:
        days_ahead = 0 - today.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        return (today + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
    
    return today.strftime('%Y-%m-%d')

def extract_time_from_text(text):
    """Extrai horário do texto"""
    
    # Padrões de horário
    time_patterns = [
        r'(\d{1,2}):(\d{2})',
        r'(\d{1,2})h(\d{2})',
        r'(\d{1,2})h',
        r'às (\d{1,2})',
    ]
    
    for pattern in time_patterns:
        match = re.search(pattern, text)
        if match:
            if len(match.groups()) == 2:
                hour, minute = match.groups()
                return f"{int(hour):02d}:{int(minute):02d}"
            else:
                hour = match.group(1)
                return f"{int(hour):02d}:00"
    
    return '14:00'

def extract_dosage_from_text(text, medication):
    """Extrai dosagem do texto"""
    
    dosage_patterns = [
        r'(\d+)mg',
        r'(\d+) mg',
        r'(\d+)g',
    ]
    
    for pattern in dosage_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return f"{match.group(1)}mg"
    
    return "Conforme prescrição"

def extract_frequency_from_text(text):
    """Extrai frequência do texto"""
    
    text_lower = text.lower()
    
    frequency_map = {
        '8/8h': '8/8h',
        '8 em 8': '8/8h',
        '12/12h': '12/12h',
        '12 em 12': '12/12h',
        '6/6h': '6/6h',
        '6 em 6': '6/6h',
        'uma vez': '24/24h',
        'duas vezes': '12/12h',
        'três vezes': '8/8h',
        'manhã': '24/24h'
    }
    
    for pattern, freq in frequency_map.items():
        if pattern in text_lower:
            return freq
    
    return '8/8h'

def generate_medication_schedule(text):
    """Gera horários dos medicamentos"""
    
    frequency = extract_frequency_from_text(text)
    
    if frequency == '8/8h':
        return ['08:00', '16:00', '00:00']
    elif frequency == '12/12h':
        return ['08:00', '20:00']
    elif frequency == '6/6h':
        return ['06:00', '12:00', '18:00', '00:00']
    elif frequency == '24/24h':
        return ['08:00']
    
    return ['08:00', '16:00']

def save_schedule_to_chromadb(user_input, event_data):
    """Salva dados no ChromaDB"""
    
    if not SERVICES_AVAILABLE:
        return
    
    try:
        chromadb_service = get_chromadb_service()
        
        # Preparar conteúdo para busca semântica
        content = f"Solicitação de agenda: {user_input}\n"
        
        if event_data.get('eventos'):
            content += "Eventos identificados:\n"
            for event in event_data['eventos']:
                content += f"- {event.get('titulo', 'N/A')}: {event.get('data', 'N/A')} às {event.get('horario', 'N/A')}\n"
        
        if event_data.get('medicamentos'):
            content += "Medicamentos identificados:\n"
            for med in event_data['medicamentos']:
                content += f"- {med.get('nome', 'N/A')}: {med.get('dosagem', 'N/A')} {med.get('frequencia', 'N/A')}\n"
        
        # Preparar metadados
        metadata = {
            'source_app': 'app2_smart_scheduler',
            'input_type': 'natural_language',
            'category': event_data.get('categoria_principal', 'unknown'),
            'ai_processed': event_data.get('ai_processed', False),
            'confidence': event_data.get('confianca', 0.5),
            'created_date': datetime.now().isoformat()
        }
        
        # Adicionar ao ChromaDB
        doc_id = f"app2_schedule_{int(time.time())}"
        
        chromadb_service.add_document(
            doc_id=doc_id,
            content=content,
            metadata=metadata
        )
        
        logger.info(f"✅ Dados salvos no ChromaDB: {doc_id}")
        
    except Exception as e:
        logger.error(f"Erro ao salvar no ChromaDB: {e}")

def save_schedule_to_sqlite(event_data):
    """Salva metadados no SQLite"""
    
    if not SERVICES_AVAILABLE:
        return
    
    try:
        sqlite_service = get_sqlite_service()
        
        # Preparar dados para SQLite
        schedule_data = {
            'app_source': 'app2_smart_scheduler',
            'input_text': event_data.get('original_text', ''),
            'events_count': len(event_data.get('eventos', [])),
            'medications_count': len(event_data.get('medicamentos', [])),
            'ai_processed': event_data.get('ai_processed', False),
            'confidence_score': event_data.get('confianca', 0.5),
            'category': event_data.get('categoria_principal', 'unknown'),
            'metadata_json': json.dumps(event_data)
        }
        
        # Salvar no SQLite
        sqlite_service.save_schedule_metadata(schedule_data)
        
        logger.info(f"✅ Metadados salvos no SQLite")
        
    except Exception as e:
        logger.error(f"Erro ao salvar no SQLite: {e}")

def create_events_from_analysis(event_data, original_text):
    """Cria eventos baseados nos dados da IA"""
    
    events_created = []
    
    # Processar eventos
    for event_info in event_data.get('eventos', []):
        event = {
            'id': f"ai_{len(st.session_state.app2_events)}_{int(time.time())}",
            'title': f"{get_event_icon(event_info['tipo'])} {event_info.get('titulo', 'Evento')}",
            'date': parse_relative_date(event_info.get('data', date.today().strftime('%Y-%m-%d'))),
            'time': event_info.get('horario', '14:00'),
            'type': event_info.get('tipo', 'outro'),
            'category': event_info.get('tipo', 'Outro').title(),
            'priority': event_info.get('prioridade', 'media').title(),
            'description': event_info.get('descricao', original_text),
            'duration': event_info.get('duracao', 60),
            'location': event_info.get('local', ''),
            'professional': event_info.get('profissional', ''),
            'observations': event_info.get('observacoes', ''),
            'created_at': datetime.now(),
            'source': 'ai_analysis',
            'ai_processed': event_data.get('ai_processed', False),
            'ai_confidence': event_data.get('confianca', 0.5)
        }
        
        st.session_state.app2_events.append(event)
        events_created.append(event)
    
    # Processar medicamentos como eventos recorrentes
    for med_info in event_data.get('medicamentos', []):
        for i, horario in enumerate(med_info.get('horarios', ['08:00'])):
            event = {
                'id': f"med_{len(st.session_state.app2_events)}_{int(time.time())}_{i}",
                'title': f"💊 {med_info.get('nome', 'Medicamento')} - {med_info.get('dosagem', '')}",
                'date': date.today().strftime('%Y-%m-%d'),
                'time': horario,
                'type': 'medicamento',
                'category': 'Medicamento',
                'priority': 'Alta',
                'description': f"Tomar {med_info.get('nome', 'medicamento')} {med_info.get('dosagem', '')} - {med_info.get('frequencia', '')}",
                'duration': 5,
                'frequency': med_info.get('frequencia', ''),
                'medication_name': med_info.get('nome', ''),
                'dosage': med_info.get('dosagem', ''),
                'created_at': datetime.now(),
                'source': 'ai_medication',
                'ai_processed': event_data.get('ai_processed', False),
                'ai_confidence': event_data.get('confianca', 0.5)
            }
            
            st.session_state.app2_events.append(event)
            events_created.append(event)
    
    return events_created

def get_event_icon(event_type):
    """Retorna ícone baseado no tipo de evento"""
    
    icons = {
        'consulta': '👨‍⚕️',
        'exame': '🩺',
        'medicamento': '💊',
        'tratamento': '🏥',
        'quimioterapia': '💉',
        'radioterapia': '☢️',
        'outro': '📅'
    }
    
    return icons.get(event_type, '📅')

def parse_relative_date(date_str):
    """Converte datas relativas para formato absoluto"""
    
    if not date_str:
        return date.today().strftime('%Y-%m-%d')
    
    if date_str in ['hoje', 'today']:
        return date.today().strftime('%Y-%m-%d')
    elif date_str in ['amanha', 'amanhã', 'tomorrow']:
        return (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
    elif date_str == 'segunda':
        days_ahead = 0 - date.today().weekday()
        if days_ahead <= 0:
            days_ahead += 7
        return (date.today() + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
    
    # Se já está no formato correto, retornar
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return date_str
    except:
        return date.today().strftime('%Y-%m-%d')

def process_with_simulation(user_input):
    """Processamento rápido sem IA"""
    
    event_data = analyze_text_simulation(user_input)
    events_created = create_events_from_analysis(event_data, user_input)
    
    if events_created:
        st.success(f"⚡ {len(events_created)} evento(s) criado(s) rapidamente!")
        
        with st.expander("👁️ Eventos Criados", expanded=True):
            for event in events_created:
                show_event_preview(event)
    else:
        st.warning("Nenhum evento foi identificado no texto")

def show_event_preview(event):
    """Mostra preview de um evento"""
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write(f"**{event['title']}**")
        st.write(f"📅 {event['date']}")
        
    with col2:
        st.write(f"⏰ {event['time']}")
        st.write(f"📊 {event['priority']}")
        
    with col3:
        if event.get('ai_processed'):
            confidence = event.get('ai_confidence', 0.5)
            st.success(f"🤖 IA ({confidence*100:.0f}%)")
        else:
            st.info("⚡ Rápido")

def show_calendar_view_section():
    """Seção de visualização do calendário"""
    
    st.markdown("#### 📅 Visualização da Agenda")
    
    if not st.session_state.app2_events:
        st.info("📋 Nenhum evento foi criado ainda. Use a aba 'Criar com IA' para começar.")
        return
    
    # Controles de visualização
    col1, col2, col3 = st.columns(3)
    
    with col1:
        view_mode = st.selectbox("👁️ Visualização:", 
                                ["📅 Lista", "📊 Por Categoria", "⏰ Por Horário"])
    
    with col2:
        date_filter = st.date_input("📅 Data:", value=date.today())
    
    with col3:
        category_filter = st.selectbox("🏷️ Categoria:", 
                                     ["Todas"] + list(set(event['category'] for event in st.session_state.app2_events)))
    
    # Filtrar eventos
    filtered_events = filter_events(date_filter, category_filter)
    
    if not filtered_events:
        st.info(f"📋 Nenhum evento encontrado para {date_filter.strftime('%d/%m/%Y')}")
        return
    
    # Mostrar eventos baseado no modo de visualização
    if view_mode == "📅 Lista":
        show_events_list(filtered_events)
    elif view_mode == "📊 Por Categoria":
        show_events_by_category(filtered_events)
    elif view_mode == "⏰ Por Horário":
        show_events_by_time(filtered_events)

def filter_events(date_filter, category_filter):
    """Filtra eventos baseado nos critérios"""
    
    filtered = []
    
    for event in st.session_state.app2_events:
        # Filtro por data
        event_date = datetime.strptime(event['date'], '%Y-%m-%d').date()
        if event_date != date_filter:
            continue
        
        # Filtro por categoria
        if category_filter != "Todas" and event['category'] != category_filter:
            continue
        
        filtered.append(event)
    
    # Ordenar por horário
    return sorted(filtered, key=lambda x: x['time'])

def show_events_list(events):
    """Mostra eventos em lista"""
    
    st.markdown(f"##### 📋 {len(events)} evento(s) encontrado(s)")
    
    for i, event in enumerate(events):
        with st.expander(f"{event['title']} - {event['time']}", expanded=False):
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Categoria:** {event['category']}")
                st.write(f"**Prioridade:** {event['priority']}")
                st.write(f"**Duração:** {event.get('duration', 60)} min")
                
                if event.get('ai_processed'):
                    confidence = event.get('ai_confidence', 0.5)
                    st.success(f"🤖 Criado por IA ({confidence*100:.0f}%)")
                else:
                    st.info("⚡ Criado rapidamente")
            
            with col2:
                if event.get('description'):
                    st.write(f"**Descrição:** {event['description']}")
                if event.get('professional'):
                    st.write(f"**Profissional:** {event['professional']}")
                if event.get('location'):
                    st.write(f"**Local:** {event['location']}")

def show_events_by_category(events):
    """Mostra eventos agrupados por categoria"""
    
    # Agrupar por categoria
    categories = {}
    for event in events:
        category = event['category']
        if category not in categories:
            categories[category] = []
        categories[category].append(event)
    
    # Mostrar cada categoria
    for category, cat_events in categories.items():
        st.markdown(f"#### {category} ({len(cat_events)} eventos)")
        
        for event in cat_events:
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.write(f"**{event['title']}**")
                if event.get('description'):
                    st.caption(event['description'][:100] + "..." if len(event['description']) > 100 else event['description'])
            
            with col2:
                st.write(f"⏰ {event['time']}")
                st.write(f"📊 {event['priority']}")
            
            with col3:
                if event.get('ai_processed'):
                    st.success("🤖 IA")
                else:
                    st.info("⚡ Rápido")

def show_events_by_time(events):
    """Mostra eventos ordenados por horário"""
    
    st.markdown("##### ⏰ Agenda do Dia")
    
    # Criar timeline
    for event in events:
        # Calcular cor baseada na prioridade
        if event['priority'] == 'Alta':
            color = '🔴'
        elif event['priority'] == 'Média':
            color = '🟡'
        else:
            color = '🟢'
        
        st.markdown(f"""
        **{event['time']}** {color} **{event['title']}**
        
        📍 {event.get('location', 'Local não informado')} | ⏱️ {event.get('duration', 60)} min
        
        ---
        """)

def show_ai_chat_section():
    """Seção de chat com IA sobre a agenda"""
    
    st.markdown("#### 💬 Chat sobre sua Agenda")
    
    if not st.session_state.app2_events:
        st.info("📋 Crie alguns eventos primeiro para conversar sobre sua agenda.")
        return
    
    # Inicializar histórico de chat
    if 'app2_chat_history' not in st.session_state:
        st.session_state.app2_chat_history = []
    
    # Mostrar histórico de chat
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.app2_chat_history[-10:]:  # Últimas 10 mensagens
            if message['role'] == 'user':
                st.chat_message("user").write(message['content'])
            else:
                st.chat_message("assistant").write(message['content'])
    
    # Input do usuário
    user_question = st.chat_input("Pergunte sobre sua agenda...")
    
    if user_question:
        # Adicionar mensagem do usuário
        st.session_state.app2_chat_history.append({
            'role': 'user',
            'content': user_question,
            'timestamp': datetime.now()
        })
        
        # Gerar resposta com IA
        response = generate_ai_agenda_response(user_question)
        
        # Adicionar resposta da IA
        st.session_state.app2_chat_history.append({
            'role': 'assistant',
            'content': response,
            'timestamp': datetime.now()
        })
        
        st.rerun()

def generate_ai_agenda_response(question):
    """Gera resposta sobre agenda usando IA real"""
    
    if not SERVICES_AVAILABLE:
        return generate_simulated_agenda_response(question)
    
    try:
        openai_service = get_openai_service()
        
        # Preparar contexto da agenda
        context = "Agenda do usuário:\n"
        
        # Eventos de hoje
        today_events = [event for event in st.session_state.app2_events 
                       if event['date'] == date.today().strftime('%Y-%m-%d')]
        
        if today_events:
            context += "Eventos de hoje:\n"
            for event in today_events:
                context += f"- {event['time']}: {event['title']} ({event['category']})\n"
        
        # Próximos eventos
        upcoming_events = [event for event in st.session_state.app2_events 
                          if event['date'] > date.today().strftime('%Y-%m-%d')][:5]
        
        if upcoming_events:
            context += "\nPróximos eventos:\n"
            for event in upcoming_events:
                context += f"- {event['date']} {event['time']}: {event['title']}\n"
        
        # Prompt para o chat
        prompt = f"""
        Você é um assistente de agenda médica especializado em oncologia.
        
        {context}
        
        Pergunta do usuário: {question}
        
        Responda de forma útil e organizada sobre a agenda do usuário.
        Se a pergunta for sobre medicamentos, seja específico sobre horários e dosagens.
        Se for sobre compromissos, mencione horários e locais quando disponível.
        """
        
        response = openai_service.generate_text(
            prompt=prompt,
            max_tokens=500,
            temperature=0.3
        )
        
        return f"🤖 {response}\n\n*Resposta gerada por IA baseada em sua agenda*"
        
    except Exception as e:
        logger.error(f"Erro na geração de resposta: {e}")
        return f"❌ Erro na IA: {e}\n\nUsando resposta simulada:\n{generate_simulated_agenda_response(question)}"

def generate_simulated_agenda_response(question):
    """Gera resposta simulada sobre agenda"""
    
    question_lower = question.lower()
    
    today_events = [event for event in st.session_state.app2_events 
                   if event['date'] == date.today().strftime('%Y-%m-%d')]
    
    if any(word in question_lower for word in ['hoje', 'agora', 'próximo']):
        if today_events:
            response = "📅 **Agenda de hoje:**\n"
            for event in sorted(today_events, key=lambda x: x['time']):
                response += f"• {event['time']} - {event['title']}\n"
            return response
        else:
            return "📅 Você não tem eventos programados para hoje."
    
    elif any(word in question_lower for word in ['medicamento', 'remedio', 'tomar']):
        today_meds = [event for event in today_events if event['type'] == 'medicamento']
        if today_meds:
            response = "💊 **Medicamentos de hoje:**\n"
            for med in sorted(today_meds, key=lambda x: x['time']):
                response += f"• {med['time']} - {med['title']}\n"
            return response
        else:
            return "💊 Nenhum medicamento programado para hoje."
    
    else:
        total_events = len(st.session_state.app2_events)
        return f"📊 Você tem {total_events} evento(s) programado(s). Sobre o que específico gostaria de saber?"

def show_integration_section():
    """Seção de integração com outros apps"""
    
    st.markdown("#### 🔗 Integração FASE 2C")
    
    # Integração com App 1
    st.markdown("##### 📤 Integração com App 1 (Document Analyzer)")
    
    # Verificar dados do App 1
    if 'app1_documents' in st.session_state and st.session_state.app1_documents:
        auto_events = integrate_with_app1_documents()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"📄 Documentos do App 1: {len(st.session_state.app1_documents)}")
            
            # Mostrar últimos documentos
            for doc in st.session_state.app1_documents[-3:]:
                st.write(f"• {doc['filename']}")
        
        with col2:
            st.info(f"📅 Eventos sugeridos: {len(auto_events)}")
            
            if auto_events and st.button("🚀 Criar Eventos Automaticamente"):
                # Verificar duplicatas
                existing_ids = {event['id'] for event in st.session_state.app2_events}
                new_events = [event for event in auto_events if event['id'] not in existing_ids]
                
                if new_events:
                    st.session_state.app2_events.extend(new_events)
                    st.success(f"✅ {len(new_events)} eventos criados automaticamente!")
                    st.rerun()
                else:
                    st.info("Todos os eventos já foram criados")
    else:
        st.info("📋 Nenhum documento encontrado no App 1. Processe documentos lá primeiro.")

def check_app1_integration():
    """Verifica integração automática com App 1"""
    
    if 'app1_integration_checked' not in st.session_state:
        st.session_state.app1_integration_checked = False
    
    if not st.session_state.app1_integration_checked:
        auto_events = integrate_with_app1_documents()
        
        if auto_events:
            # Verificar se eventos já existem para evitar duplicatas
            existing_ids = {event['id'] for event in st.session_state.app2_events}
            new_events = [event for event in auto_events if event['id'] not in existing_ids]
            
            if new_events:
                st.session_state.app2_events.extend(new_events)
                
                st.sidebar.success(f"✅ {len(new_events)} eventos criados automaticamente do App 1!")
                
                with st.sidebar.expander("Ver eventos criados"):
                    for event in new_events:
                        st.write(f"• {event['title']} - {event['date']}")
        
        st.session_state.app1_integration_checked = True

def integrate_with_app1_documents():
    """Integra dados do App 1 automaticamente"""
    
    auto_events = []
    
    if 'app1_documents' in st.session_state:
        for doc in st.session_state.app1_documents:
            extraction = doc.get('extraction', {})
            
            # Verificar eventos sugeridos
            for suggested_event in extraction.get('eventos_sugeridos', []):
                
                if suggested_event.get('tipo') == 'medicamento':
                    # Criar evento de medicamento
                    auto_event = {
                        'id': f"auto_med_{doc['id']}_{suggested_event.get('titulo', 'med')}",
                        'title': f"💊 {suggested_event['titulo']}",
                        'date': suggested_event.get('data', date.today().strftime('%Y-%m-%d')),
                        'time': suggested_event.get('horario', '08:00'),
                        'type': 'medicamento',
                        'category': 'Medicamento',
                        'priority': 'Alta',
                        'description': f"Medicamento extraído de: {doc['filename']}",
                        'created_at': datetime.now(),
                        'source': 'app1_integration'
                    }
                    
                    auto_events.append(auto_event)
                
                elif suggested_event.get('tipo') == 'consulta':
                    # Criar evento de consulta
                    auto_event = {
                        'id': f"auto_cons_{doc['id']}_{suggested_event.get('titulo', 'cons')}",
                        'title': f"👨‍⚕️ {suggested_event['titulo']}",
                        'date': suggested_event.get('data', date.today().strftime('%Y-%m-%d')),
                        'time': suggested_event.get('horario', '14:00'),
                        'type': 'consulta',
                        'category': 'Consulta',
                        'priority': 'Alta',
                        'description': f"Consulta extraída de: {doc['filename']}",
                        'created_at': datetime.now(),
                        'source': 'app1_integration'
                    }
                    
                    auto_events.append(auto_event)
    
    return auto_events

def show_events_history_section():
    """Seção de histórico de eventos"""
    
    st.markdown("#### 📊 Histórico de Eventos")
    
    if not st.session_state.app2_events:
        st.info("📋 Nenhum evento foi criado ainda.")
        return
    
    # Métricas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_events = len(st.session_state.app2_events)
        st.metric("📅 Total", total_events)
    
    with col2:
        ai_events = len([e for e in st.session_state.app2_events if e.get('ai_processed', False)])
        st.metric("🤖 IA Real", ai_events)
    
    with col3:
        med_events = len([e for e in st.session_state.app2_events if e['type'] == 'medicamento'])
        st.metric("💊 Medicamentos", med_events)
    
    with col4:
        consultation_events = len([e for e in st.session_state.app2_events if e['type'] == 'consulta'])
        st.metric("👨‍⚕️ Consultas", consultation_events)

def main():
    """Função principal para compatibilidade"""
    run_smart_scheduler()

if __name__ == "__main__":
    run_smart_scheduler()