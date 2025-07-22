import os
import sys
import streamlit as st
import streamlit.components.v1 as components
from sidebar import sidebar
from streamlit_option_menu import option_menu
from streamlit_autorefresh import st_autorefresh


# Corrige o sys.path para importar src.dashboard.*
sys.path.append(os.path.join(os.getcwd(), "src"))

# Agora os imports funcionam
from dashboard.home.main import main as main_home
from dashboard.dash.main import main as main_dash

# Configurações iniciais
st.set_page_config(
    page_title='DASH CRD',
    page_icon="📊",
    layout='wide',
    menu_items={
        'Get Help': 'https://wa.me/5581997293669',
        'Report a bug': 'https://wa.me/5581997293669',
    },
)

st_autorefresh(interval=9 * 1000, key="auto_refresh")

# Oculta o menu padrão do Streamlit
st.markdown("""
    <style>
        header {visibility: hidden;}
        [data-testid="stSidebarNav"] > ul {
            display: none;
        }
    </style>
""", unsafe_allow_html=True)

# Inicializa a página se ainda não existir
if "page" not in st.session_state:
    st.session_state.page = "Página Inicial"

# 👉 Chama a sidebar primeiro
sidebar()

# Menu horizontal principal
selecionado = option_menu(
    menu_title=None,
    options=["Página Inicial","Dashboard"],
    icons=["house", "book","bar-chart"],
    menu_icon="cast",
    default_index=["Página Inicial", "Dashboard"].index(st.session_state.page),
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#00332e"},
        "icon": {"color": "white", "font-size": "18px"},
        "nav-link": {
            "font-size": "16px",
            "text-align": "center",
            "margin": "0px",
            "color": "white",
        },
        "nav-link-selected": {
            "background-color": "#145c52",
            "font-weight": "bold",
        },
    }
)

# Sincroniza com session_state, se necessário
if selecionado != st.session_state.page:
    st.session_state.page = selecionado
    st.rerun()

# 🚀 Executa a página escolhida
if st.session_state.page == "Página Inicial":
    main_home()
elif st.session_state.page == "Dashboard":
    main_dash()