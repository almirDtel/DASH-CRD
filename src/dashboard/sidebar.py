import streamlit as st
from streamlit_option_menu import option_menu

def sidebar():
    with st.sidebar:
        st.title("Painel de Navegação")

        opcao = option_menu(
            menu_title=None,
            options=["Página Inicial",  "Dashboard"],
            icons=["house",  "bar-chart"],
            menu_icon="cast",
            default_index=["Página Inicial", "Dashboard"].index(st.session_state.page),
        )

        if opcao != st.session_state.page:
            st.session_state.page = opcao
            st.rerun()

        st.markdown("---")
        st.markdown("### ☕ Suporte")
        st.markdown("""
        <a href="https://wa.me/5581997293669" target="_blank" style="
            display: inline-block;
            background-color: #25D366;
            color: white;
            padding: 12px 24px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: bold;
            font-size: 1.1rem;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
            margin-top: 10px;
        ">
            <span style="font-size:1.3rem;">💬</span> Suporte via WhatsApp
        </a>
        """, unsafe_allow_html=True)
