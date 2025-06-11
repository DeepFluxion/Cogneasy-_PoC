'''
App 3: Document Chat - RAG Real
'''

import streamlit as st
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    '''Interface principal do App 3 com RAG real'''
    
    st.title("💬 Document Chat - RAG Real")
    st.markdown("**Consulte a base de conhecimento médica usando IA real**")
    
    # Inicializar serviços
    if "chat_manager" not in st.session_state:
        st.session_state.chat_manager = None
        st.session_state.session_id = None
        st.session_state.initialization_attempted = False
    
    if not st.session_state.initialization_attempted:
        success = initialize_real_services()
        st.session_state.initialization_attempted = True
        
        if not success:
            st.error("⚠️ Sistema em modo limitado")
            st.info("💡 Configure OpenAI e execute validação Sessão 1")
    
    # Interface
    if st.session_state.chat_manager and st.session_state.chat_manager.is_available():
        render_real_chat_interface()
    else:
        render_fallback_interface()

def initialize_real_services() -> bool:
    '''Inicializa serviços reais'''
    try:
        from .chat_manager import get_chat_manager
        
        chat_manager = get_chat_manager()
        
        if chat_manager.is_available():
            st.session_state.chat_manager = chat_manager
            
            if not st.session_state.session_id:
                st.session_state.session_id = chat_manager.create_session("streamlit_user")
            
            st.success("✅ Sistema RAG real inicializado!")
            return True
        else:
            st.warning("⚠️ RAG Engine não disponível")
            return False
            
    except Exception as e:
        st.error(f"❌ Erro na inicialização: {e}")
        return False

def render_real_chat_interface():
    '''Interface de chat usando RAG real'''
    
    chat_manager = st.session_state.chat_manager
    session_id = st.session_state.session_id
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 Sistema RAG Real")
        
        try:
            documents = chat_manager.get_available_documents()
            
            with st.expander("📚 Base de Conhecimento", expanded=True):
                if documents:
                    for doc in documents:
                        st.markdown(f"• {doc['name']}")
                else:
                    st.info("Carregando documentos...")
                    
        except Exception as e:
            st.error(f"Erro: {e}")
        
        # Perguntas sugeridas
        with st.expander("💡 Perguntas Sugeridas"):
            questions = chat_manager.get_suggested_questions()
            
            for question in questions[:5]:
                if st.button(question, key=f"suggested_{hash(question)}"):
                    st.session_state.suggested_question = question
                    st.experimental_rerun()
    
    # Área principal
    messages_container = st.container()
    
    # Histórico
    try:
        history = chat_manager.get_session_history(session_id)
        
        with messages_container:
            for msg in history:
                if msg["type"] == "user":
                    with st.chat_message("user"):
                        st.write(msg["message"])
                elif msg["type"] == "assistant":
                    with st.chat_message("assistant"):
                        st.markdown(msg["message"])
    
    except Exception as e:
        st.error(f"Erro no histórico: {e}")
    
    # Input
    user_input = st.chat_input("Digite sua pergunta médica...")
    
    if "suggested_question" in st.session_state:
        user_input = st.session_state.suggested_question
        del st.session_state.suggested_question
    
    if user_input:
        process_user_message(chat_manager, session_id, user_input)

def process_user_message(chat_manager, session_id, message):
    '''Processa mensagem do usuário'''
    
    with st.chat_message("user"):
        st.write(message)
    
    with st.chat_message("assistant"):
        with st.spinner("🔍 Consultando base..."):
            try:
                response = chat_manager.send_message(session_id, message)
                
                if "error" in response:
                    st.error(response["response"])
                else:
                    st.markdown(response["response"])
                    
                    if response.get("confidence", 0) > 0:
                        with st.expander("📊 Detalhes", expanded=False):
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("Confiança", f"{response['confidence']:.1%}")
                            with col2:
                                st.metric("Documentos", response.get('relevant_documents', 0))
                            with col3:
                                st.metric("Tempo", f"{response.get('response_time', 0):.2f}s")
                
            except Exception as e:
                st.error(f"Erro: {e}")

def render_fallback_interface():
    '''Interface de fallback'''
    
    st.warning("🔧 Sistema em Modo Limitado")
    st.info('''
    Para ativar RAG real:
    1. Configure OPENAI_API_KEY
    2. Execute: python validation_session1.py  
    3. Verifique taxa ≥ 75%
    ''')
    
    user_input = st.text_input("Sua pergunta:")
    
    if user_input and st.button("Enviar"):
        st.markdown(f"**Você:** {user_input}")
        st.markdown("**Sistema:** Sistema limitado. Consulte sua equipe médica.")

if __name__ == "__main__":
    main()
