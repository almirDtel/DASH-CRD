import streamlit as st
from pathlib import Path


def main():

    st.markdown("<h1 style='text-align: center; color: #3498db;'>📡 Ingestão Inteligente de Dados via API</h1>", unsafe_allow_html=True)

    st.markdown("<h4 style='text-align: center; color: #ccc;'>Automatize a coleta, tratamento e análise de dados com segurança e escalabilidade</h4>", unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("### 📌 Sobre o projeto")
    st.markdown("""
    Este projeto foi desenvolvido com foco na automação da **extração de dados de APIs**, transformações customizadas e exibição em dashboards interativos.
    
    Ele utiliza uma arquitetura limpa com separação entre:
    - Autenticação e consumo de APIs
    - Transformação dos dados
    - Salvamento em arquivos locais (ou base de dados futuramente)
    """)

    st.markdown("---")

    st.markdown("### ⚙️ Funcionalidades principais")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🔐 Autenticação Segura")
        st.markdown("""
        - Leitura segura de credenciais com `.env`
        - Sessão com chave de API
        - Validação automática antes de cada requisição
        """)

        st.markdown("#### 📈 Extração de Dados")
        st.markdown("""
        - Requisições GET com parâmetros dinâmicos
        - Coleta de múltiplos endpoints
        - Controle de período (data inicial/final, filtros, etc)
        """)

    with col2:
        st.markdown("#### 🧠 Transformação dos Dados")
        st.markdown("""
        - Funções reutilizáveis para limpeza e estruturação
        - Merge com outras fontes (ex: agentes online)
        - Padronização de colunas
        """)

        st.markdown("#### 💾 Exportação")
        st.markdown("""
        - Exporta para `.csv` automaticamente
        - Pode ser adaptado para bancos SQL
        - Ideal para integrar com dashboards
        """)

    st.markdown("---")

    st.markdown("---")
    st.markdown("### 👨‍💻 Desenvolvido por")
    st.markdown("""
    - Almir Soares
    """)

    st.markdown("<p style='text-align:center; color: #aaa;'>Projeto de Ingestão via API - Automatize e acelere sua operação com dados confiáveis.</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
