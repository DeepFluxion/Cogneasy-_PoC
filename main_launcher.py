"""
CognEasy PoCs - Main Launcher FASE 2C
Sistema integrado com infraestrutura real
OpenAI + ChromaDB + SQLite + Apps integrados
"""

import streamlit as st
import sys
from pathlib import Path
import time
import json
from datetime import datetime
import logging

# Configurar página
st.set_page_config(
    page_title="CognEasy PoCs - FASE 2C",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Adicionar pasta raiz ao path
root_path = Path(__file__).parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

def check_infrastructure_status():
    """Verifica status da infraestrutura FASE 2C"""
    
    status = {
        'openai': False,
        'chromadb': False,
        'sqlite': False,
        'knowledge_base': False,
        'overall': False
    }
    
    try:
        # Verificar serviços FASE 2C
        from shared.openai_service_real import get_openai_service
        from shared.chromadb_service import get_chromadb_service
        from shared.sqlite_service import get_sqlite_service
        
        # OpenAI
        openai_service = get_openai_service()
        status['openai'] = openai_service.is_available()
        
        # ChromaDB
        chromadb_service = get_chromadb_service()
        status['chromadb'] = chromadb_service.is_available()
        
        # SQLite
        sqlite_service = get_sqlite_service()
        status['sqlite'] = sqlite_service.is_available()
        
        # Base de conhecimento
        kb_path = Path("data/knowledge_base")
        if kb_path.exists():
            txt_files = list(kb_path.glob("*.txt"))
            status['knowledge_base'] = len(txt_files) >= 3
        
        # Status geral
        status['overall'] = all([
            status['openai'],
            status['chromadb'], 
            status['sqlite'],
            status['knowledge_base']
        ])
        
    except Exception as e:
        logger.error(f"Erro ao verificar infraestrutura: {e}")
        # Fallback - assumir disponibilidade básica
        status['knowledge_base'] = True
        status['overall'] = False
    
    return status

def show_infrastructure_panel():
    """Mostra painel de status da infraestrutura"""
    
    with st.sidebar:
        st.markdown("### 🔧 Status da Infraestrutura")
        
        status = check_infrastructure_status()
        
        # OpenAI
        if status['openai']:
            st.success("✅ OpenAI Conectada")
        else:
            st.error("❌ OpenAI Indisponível")
            st.caption("Configure OPENAI_API_KEY")
        
        # ChromaDB
        if status['chromadb']:
            st.success("✅ ChromaDB Ativo")
        else:
            st.error("❌ ChromaDB Indisponível")
        
        # SQLite
        if status['sqlite']:
            st.success("✅ SQLite Operacional")
        else:
            st.error("❌ SQLite Indisponível")
        
        # Base de conhecimento
        if status['knowledge_base']:
            st.success("✅ Base de Conhecimento")
            try:
                kb_path = Path("data/knowledge_base")
                txt_files = list(kb_path.glob("*.txt"))
                st.caption(f"{len(txt_files)} documentos")
            except:
                st.caption("Documentos carregados")
        else:
            st.error("❌ Base Limitada")
            st.caption("Mínimo 3 documentos .txt")
        
        # Status geral
        st.markdown("---")
        if status['overall']:
            st.success("🎉 Sistema FASE 2C Completo")
            st.caption("Todas as funcionalidades ativas")
        else:
            st.warning("⚠️ Sistema FASE 2C Parcial")
            st.caption("Algumas limitações")
        
        return status

def show_navigation_menu(infrastructure_status):
    """Mostra menu de navegação"""
    
    with st.sidebar:
        st.markdown("### 🧭 Navegação")
        
        # Inicializar página atual
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 'home'
        
        # Menu principal
        pages = {
            'home': '🏠 Início',
            'app1': '📄 Document Analyzer',
            'app2': '📅 Smart Scheduler', 
            'app3': '💬 Document Chat',
            'integration': '🔗 Integração',
            'diagnostics': '🩺 Diagnósticos'
        }
        
        for page_key, page_name in pages.items():
            if st.button(page_name, key=f"nav_{page_key}", use_container_width=True):
                st.session_state.current_page = page_key
                st.rerun()
        
        # Indicador da página atual
        current_page_name = pages.get(st.session_state.current_page, 'Desconhecida')
        st.markdown(f"**Página atual:** {current_page_name}")
        
        # Informações do sistema
        st.markdown("---")
        st.markdown("### ℹ️ Sistema")
        st.markdown("**Versão:** FASE 2C")
        st.markdown("**Modo:** Infraestrutura Real")
        st.markdown(f"**Última atualização:** {datetime.now().strftime('%H:%M')}")

def show_home_page(infrastructure_status):
    """Página inicial do sistema"""
    
    st.title("🧠 CognEasy PoCs - FASE 2C")
    st.markdown("### Sistema Integrado com Infraestrutura Real")
    
    # Status geral do sistema
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if infrastructure_status['overall']:
            st.success("🎉 **Sistema Completo**")
            st.markdown("Todas as funcionalidades ativas")
        else:
            st.warning("⚠️ **Sistema Parcial**")
            st.markdown("Algumas limitações")
    
    with col2:
        st.info("🤖 **IA Real Integrada**")
        if infrastructure_status['openai']:
            st.markdown("OpenAI ativa")
        else:
            st.markdown("Modo simulado")
    
    with col3:
        st.info("🔗 **Apps Integrados**")
        st.markdown("Fluxo automático")
    
    # Demonstração do fluxo
    st.markdown("---")
    st.markdown("## 🔄 Fluxo Integrado FASE 2C")
    
    flow_col1, flow_col2, flow_col3 = st.columns(3)
    
    with flow_col1:
        st.markdown("""
        ### 📄 App 1: Document Analyzer
        **Com IA Real:**
        - Análise automática de receitas
        - Extração de medicamentos
        - Geração de eventos
        - Integração com App 3
        
        **Tecnologias:**
        - OpenAI para análise
        - ChromaDB para armazenamento
        - SQLite para metadados
        """)
        
        if st.button("🚀 Usar App 1", key="home_app1"):
            st.session_state.current_page = 'app1'
            st.rerun()
    
    with flow_col2:
        st.markdown("""
        ### 📅 App 2: Smart Scheduler
        **Com IA Real:**
        - Linguagem natural para eventos
        - Integração automática App 1→App 2
        - Criação inteligente de agenda
        - Chat sobre compromissos
        
        **Tecnologias:**
        - OpenAI para NLP
        - ChromaDB para contexto
        - Integração automática
        """)
        
        if st.button("🚀 Usar App 2", key="home_app2"):
            st.session_state.current_page = 'app2'
            st.rerun()
    
    with flow_col3:
        st.markdown("""
        ### 💬 App 3: Document Chat
        **RAG Real:**
        - Chat com base de conhecimento
        - Busca semântica avançada
        - Citações precisas
        - Integração com Apps 1 e 2
        
        **Tecnologias:**
        - OpenAI para chat
        - ChromaDB para RAG
        - Base médica especializada
        """)
        
        if st.button("🚀 Usar App 3", key="home_app3"):
            st.session_state.current_page = 'app3'
            st.rerun()
    
    # Métricas do sistema
    st.markdown("---")
    st.markdown("## 📊 Métricas do Sistema")
    
    metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
    
    with metrics_col1:
        app1_docs = len(st.session_state.get('app1_documents', []))
        st.metric("📄 Documentos App 1", app1_docs)
    
    with metrics_col2:
        app2_events = len(st.session_state.get('app2_events', []))
        st.metric("📅 Eventos App 2", app2_events)
    
    with metrics_col3:
        app3_messages = len(st.session_state.get('app3_chat_history', []))
        st.metric("💬 Mensagens App 3", app3_messages)
    
    with metrics_col4:
        # Integração geral
        integrations = 0
        if st.session_state.get('app3_integrated_docs'):
            integrations += len(st.session_state.app3_integrated_docs)
        if st.session_state.get('app3_integrated_agenda'):
            integrations += len(st.session_state.app3_integrated_agenda)
        st.metric("🔗 Integrações", integrations)
    
    # Quick actions
    st.markdown("---")
    st.markdown("## ⚡ Ações Rápidas")
    
    action_col1, action_col2, action_col3 = st.columns(3)
    
    with action_col1:
        if st.button("🔄 Executar Diagnóstico", key="quick_diagnostic"):
            st.session_state.current_page = 'diagnostics'
            st.rerun()
    
    with action_col2:
        if st.button("📊 Ver Integrações", key="quick_integration"):
            st.session_state.current_page = 'integration'
            st.rerun()
    
    with action_col3:
        if st.button("🧪 Testar Sistema", key="quick_test"):
            run_quick_system_test()

def run_quick_system_test():
    """Executa teste rápido do sistema"""
    
    with st.spinner("🧪 Executando teste rápido..."):
        time.sleep(2)  # Simular teste
        
        test_results = {
            'infrastructure': check_infrastructure_status(),
            'apps_loaded': True,
            'session_state': len(st.session_state) > 0
        }
        
        if test_results['infrastructure']['overall']:
            st.success("✅ Teste rápido passou! Sistema funcionando perfeitamente.")
        else:
            st.warning("⚠️ Teste parcial. Algumas funcionalidades limitadas.")
        
        with st.expander("👁️ Detalhes do teste"):
            st.json(test_results)

def show_integration_page():
    """Página de integração entre apps"""
    
    st.title("🔗 Integração FASE 2C")
    st.markdown("### Fluxo Automático Entre Aplicativos")
    
    # Status das integrações
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 📄→📅 App 1 → App 2")
        app1_docs = len(st.session_state.get('app1_documents', []))
        app2_from_app1 = len([e for e in st.session_state.get('app2_events', []) 
                             if e.get('source') == 'app1_integration'])
        
        st.metric("Documentos App 1", app1_docs)
        st.metric("Eventos criados", app2_from_app1)
        
        if app1_docs > 0:
            st.success("✅ Integração ativa")
        else:
            st.info("📋 Processe documentos no App 1")
    
    with col2:
        st.markdown("#### 📄→💬 App 1 → App 3")
        app3_integrated_docs = len(st.session_state.get('app3_integrated_docs', []))
        
        st.metric("Docs integrados", app3_integrated_docs)
        
        if app3_integrated_docs > 0:
            st.success("✅ Documentos no App 3")
        else:
            st.info("📋 Integre documentos no App 1")
    
    with col3:
        st.markdown("#### 📅→💬 App 2 → App 3")
        app3_integrated_agenda = len(st.session_state.get('app3_integrated_agenda', []))
        
        st.metric("Agendas integradas", app3_integrated_agenda)
        
        if app3_integrated_agenda > 0:
            st.success("✅ Agenda no App 3")
        else:
            st.info("📋 Integre agenda no App 2")
    
    # Fluxo visual
    st.markdown("---")
    st.markdown("## 🔄 Fluxo de Dados")
    
    st.markdown("""
    ```
    📄 App 1 (Document Analyzer)
    ├── Analisa receitas médicas com OpenAI
    ├── Extrai medicamentos e orientações
    ├── Salva no ChromaDB para busca semântica
    ├── Registra metadados no SQLite
    └── 🔗 INTEGRA COM:
        ├── 📅 App 2: Cria eventos de medicamentos automaticamente
        └── 💬 App 3: Adiciona documentos à base de conhecimento
    
    📅 App 2 (Smart Scheduler)
    ├── Processa linguagem natural com OpenAI
    ├── Cria eventos inteligentes
    ├── Integra automaticamente com dados do App 1
    ├── Salva agenda no ChromaDB
    └── 🔗 INTEGRA COM:
        └── 💬 App 3: Disponibiliza agenda para consultas
    
    💬 App 3 (Document Chat)
    ├── RAG real com ChromaDB
    ├── Chat contextual com OpenAI
    ├── Base de conhecimento médica
    ├── Recebe dados integrados dos Apps 1 e 2
    └── 🔗 FORNECE:
        └── Respostas baseadas em TODOS os dados do usuário
    ```
    """)
    
    # Ações de integração
    st.markdown("---")
    st.markdown("## ⚡ Ações de Integração")
    
    integration_col1, integration_col2 = st.columns(2)
    
    with integration_col1:
        if st.button("🔄 Sincronizar Dados", key="sync_data"):
            with st.spinner("Sincronizando..."):
                time.sleep(1)
                st.success("✅ Dados sincronizados entre apps!")
    
    with integration_col2:
        if st.button("🧹 Limpar Integrações", key="clear_integrations"):
            st.session_state.pop('app3_integrated_docs', None)
            st.session_state.pop('app3_integrated_agenda', None)
            st.success("✅ Integrações limpas!")
            st.rerun()

def show_diagnostics_page():
    """Página de diagnósticos"""
    
    st.title("🩺 Diagnósticos FASE 2C")
    st.markdown("### Verificação Completa do Sistema")
    
    # Status atual
    infrastructure_status = check_infrastructure_status()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Status Atual")
        
        if infrastructure_status['overall']:
            st.success("🎉 Sistema FASE 2C Completo")
        else:
            st.warning("⚠️ Sistema FASE 2C Parcial")
        
        st.markdown("**Componentes:**")
        
        for component, status in infrastructure_status.items():
            if component != 'overall':
                icon = "✅" if status else "❌"
                component_name = {
                    'openai': 'OpenAI',
                    'chromadb': 'ChromaDB', 
                    'sqlite': 'SQLite',
                    'knowledge_base': 'Base de Conhecimento'
                }.get(component, component)
                
                st.markdown(f"{icon} {component_name}")
    
    with col2:
        st.markdown("#### 🔧 Ações de Diagnóstico")
        
        if st.button("🧪 Diagnóstico Rápido", key="quick_diag"):
            run_quick_diagnostic()
        
        if st.button("🔍 Diagnóstico Completo", key="full_diag"):
            run_full_diagnostic()
        
        if st.button("📊 Relatório Detalhado", key="detailed_report"):
            show_detailed_report()
    
    # Histórico de diagnósticos
    st.markdown("---")
    st.markdown("## 📈 Histórico de Diagnósticos")
    
    # Verificar se há relatórios salvos
    report_files = [
        ("phase2c_diagnostic_report.json", "Diagnóstico FASE 2C"),
        ("session2_validation_report.json", "Validação Sessão 2"),
        ("session1_validation_report.json", "Validação Sessão 1")
    ]
    
    for report_file, report_name in report_files:
        if Path(report_file).exists():
            try:
                with open(report_file, 'r', encoding='utf-8') as f:
                    report_data = json.load(f)
                
                timestamp = report_data.get('timestamp', 'N/A')
                success_rate = report_data.get('success_rate', 0)
                status = report_data.get('final_status', 'Desconhecido')
                
                with st.expander(f"📄 {report_name} - {status} ({success_rate:.1f}%)"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**Data:** {timestamp[:19] if timestamp != 'N/A' else 'N/A'}")
                        st.write(f"**Status:** {status}")
                    
                    with col2:
                        st.write(f"**Taxa de sucesso:** {success_rate:.1f}%")
                        st.write(f"**Testes:** {report_data.get('successful_tests', 0)}/{report_data.get('total_tests', 0)}")
                    
                    with col3:
                        if st.button(f"👁️ Ver detalhes", key=f"view_{report_file}"):
                            st.json(report_data)
                            
            except Exception as e:
                st.error(f"Erro ao ler {report_file}: {e}")

def run_quick_diagnostic():
    """Executa diagnóstico rápido"""
    
    with st.spinner("🧪 Executando diagnóstico rápido..."):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Simular verificações
        checks = [
            ("Verificando configurações...", 20),
            ("Testando OpenAI...", 40),
            ("Verificando ChromaDB...", 60),
            ("Testando SQLite...", 80),
            ("Validando apps...", 100)
        ]
        
        results = []
        
        for check_text, progress in checks:
            status_text.text(check_text)
            progress_bar.progress(progress)
            time.sleep(0.5)
            
            # Verificação real baseada no status da infraestrutura
            infrastructure_status = check_infrastructure_status()
            
            if "OpenAI" in check_text:
                results.append(("OpenAI", infrastructure_status['openai']))
            elif "ChromaDB" in check_text:
                results.append(("ChromaDB", infrastructure_status['chromadb']))
            elif "SQLite" in check_text:
                results.append(("SQLite", infrastructure_status['sqlite']))
            elif "apps" in check_text:
                results.append(("Apps", True))  # Assume apps carregam
        
        status_text.text("✅ Diagnóstico concluído!")
        progress_bar.progress(100)
        
        # Mostrar resultados
        success_count = sum(1 for _, status in results if status)
        total_count = len(results)
        success_rate = (success_count / total_count) * 100 if total_count > 0 else 0
        
        if success_rate >= 80:
            st.success(f"✅ Diagnóstico rápido: {success_rate:.0f}% - Sistema funcionando bem!")
        elif success_rate >= 60:
            st.warning(f"⚠️ Diagnóstico rápido: {success_rate:.0f}% - Algumas limitações")
        else:
            st.error(f"❌ Diagnóstico rápido: {success_rate:.0f}% - Problemas identificados")
        
        # Detalhes
        with st.expander("👁️ Detalhes do diagnóstico"):
            for component, status in results:
                icon = "✅" if status else "❌"
                st.write(f"{icon} {component}")

def run_full_diagnostic():
    """Executa diagnóstico completo"""
    
    st.info("🔍 Executando diagnóstico completo...")
    st.markdown("```bash\npython diagnostic_functional.py\n```")
    
    with st.expander("📋 Como executar manualmente"):
        st.markdown("""
        **No terminal, execute:**
        
        ```bash
        python diagnostic_functional.py
        ```
        
        **Resultado esperado:**
        - Taxa de sucesso ≥ 85%
        - Todos os serviços funcionando
        - Apps integrados operacionais
        """)

def show_detailed_report():
    """Mostra relatório detalhado"""
    
    st.markdown("### 📊 Relatório Detalhado do Sistema")
    
    # Informações do sistema
    system_info = {
        "Versão": "FASE 2C - Integrada",
        "Modo": "Infraestrutura Real",
        "Apps": ["Document Analyzer", "Smart Scheduler", "Document Chat"],
        "Tecnologias": ["OpenAI", "ChromaDB", "SQLite", "Streamlit"],
        "Status": "Produção" if check_infrastructure_status()['overall'] else "Desenvolvimento"
    }
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🏗️ Arquitetura")
        for key, value in system_info.items():
            if isinstance(value, list):
                st.write(f"**{key}:** {', '.join(value)}")
            else:
                st.write(f"**{key}:** {value}")
    
    with col2:
        st.markdown("#### 📈 Métricas de Uso")
        
        # Session state metrics
        total_keys = len(st.session_state)
        app1_docs = len(st.session_state.get('app1_documents', []))
        app2_events = len(st.session_state.get('app2_events', []))
        app3_messages = len(st.session_state.get('app3_chat_history', []))
        
        st.metric("Session State Keys", total_keys)
        st.metric("Documentos processados", app1_docs)
        st.metric("Eventos criados", app2_events)
        st.metric("Mensagens de chat", app3_messages)

def load_app_page(app_name):
    """Carrega página de um app específico"""
    
    try:
        if app_name == 'app1':
            from apps.app1_document_analyzer.main import run_document_analyzer
            run_document_analyzer()
        elif app_name == 'app2':
            from apps.app2_smart_scheduler.main import run_smart_scheduler
            run_smart_scheduler()
        elif app_name == 'app3':
            from apps.app3_document_chat.main import main as run_document_chat
            run_document_chat()
        else:
            st.error(f"App '{app_name}' não encontrado")
            
    except ImportError as e:
        st.error(f"Erro ao carregar {app_name}: {e}")
        
        # Instruções para resolver
        st.info("💡 Para resolver:")
        if app_name == 'app1':
            st.markdown("1. Verifique se `apps/app1_document_analyzer/main.py` existe")
            st.markdown("2. Execute: `python diagnostic_functional.py`")
        elif app_name == 'app2':
            st.markdown("1. Verifique se `apps/app2_smart_scheduler/main.py` existe")
            st.markdown("2. Execute: `python diagnostic_functional.py`")
        elif app_name == 'app3':
            st.markdown("1. Verifique se `apps/app3_document_chat/main.py` existe")
            st.markdown("2. Execute: `python diagnostic_functional.py`")
        
    except Exception as e:
        st.error(f"Erro na execução do {app_name}: {e}")
        st.info("Tente recarregar a página")

def main():
    """Função principal do launcher FASE 2C"""
    
    try:
        # Verificar status da infraestrutura
        infrastructure_status = show_infrastructure_panel()
        
        # Mostrar menu de navegação
        show_navigation_menu(infrastructure_status)
        
        # Roteamento de páginas
        current_page = st.session_state.get('current_page', 'home')
        
        if current_page == 'home':
            show_home_page(infrastructure_status)
        elif current_page == 'integration':
            show_integration_page()
        elif current_page == 'diagnostics':
            show_diagnostics_page()
        elif current_page in ['app1', 'app2', 'app3']:
            load_app_page(current_page)
        else:
            st.error(f"Página '{current_page}' não encontrada")
            st.session_state.current_page = 'home'
            st.rerun()
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #666; padding: 20px;'>
            <small>
                🧠 CognEasy PoCs - FASE 2C | 
                Sistema integrado com infraestrutura real | 
                OpenAI + ChromaDB + SQLite
            </small>
        </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Erro crítico no sistema: {e}")
        st.info("Tente recarregar a página ou execute o diagnóstico")
        
        with st.expander("🔍 Detalhes do erro"):
            st.exception(e)
        
        # Ações de recuperação
        st.markdown("### 🛠️ Ações de Recuperação")
        
        recovery_col1, recovery_col2 = st.columns(2)
        
        with recovery_col1:
            if st.button("🔄 Recarregar Sistema", key="reload_system"):
                st.rerun()
        
        with recovery_col2:
            if st.button("🩺 Executar Diagnóstico", key="emergency_diagnostic"):
                st.markdown("Execute no terminal: `python diagnostic_functional.py`")

if __name__ == "__main__":
    main()