import streamlit as st
import sys
import os

# Adiciona a pasta ao path e importa
sys.path.append(os.path.join(os.getcwd(), "monitoramento CRD"))
from app import main as main_home

# Executa a lógica da página inicial
main_home()