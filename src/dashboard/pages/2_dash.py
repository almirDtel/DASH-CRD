import streamlit as st
import sys
import os

# Adiciona a pasta ao path e importa
sys.path.append(os.path.join(os.getcwd(), "dash"))
from app import main as main_dash

# Executa a lógica da página de dashboard
main_dash()