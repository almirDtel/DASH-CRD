import os
import pandas as pd
import pymysql
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Carrega o .env a partir da raiz do projeto
dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))
load_dotenv(dotenv_path)

# Configuração do banco
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = int(os.getenv("DB_PORT"))

def get_ligacoes_por_data(conn, data_inicio, data_fim):
    query = """
        SELECT data_hora, agente, status 
        FROM monitoramento_ligacoes 
        WHERE data_hora BETWEEN %s AND %s
    """
    try:
        return pd.read_sql(query, conn, params=[data_inicio, data_fim])
    except Exception:
        return pd.DataFrame()

def get_pesquisa_por_data(conn, data_inicio, data_fim):
    query = """
        SELECT nom_pergunta, agente, dat_resposta, nom_valor
        FROM pesquisa_analitico 
        WHERE dat_resposta BETWEEN %s AND %s
    """
    try:
        return pd.read_sql(query, conn, params=[data_inicio, data_fim])
    except Exception:
        return pd.DataFrame()

def get_asana(conn):
    query = """
        SELECT cidade, olt, status, total_clientes_afetados, impacto
        FROM tasks_asana 
    """
    try:
        return pd.read_sql(query, conn)
    except Exception:
        return pd.DataFrame()
    
def get_agentes_online(conn):
    query = """
        SELECT agente, pausa, status, tempo_status, tempo_logado, dat_login
        FROM agentes_online 
    """
    try:
        return pd.read_sql(query, conn)
    except Exception:
        return pd.DataFrame()
    
def get_estatistico_instataneo(conn):
    query = """
        SELECT agente, servico, tmia, tma, num_qtd
        FROM estatistico_atendimento_instantaneo 
    """
    try:
        return pd.read_sql(query, conn)
    except Exception:
        return pd.DataFrame()


def get_db(data_inicio, data_fim):
    """Abre a conexão, executa as consultas e fecha a conexão."""
    try:
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT,
            cursorclass=pymysql.cursors.Cursor
        )
        try:
            df_ligacoes = get_ligacoes_por_data(conn, data_inicio, data_fim)
            df_asana = get_asana(conn)
            df_online = get_agentes_online(conn)
            df_estatistico = get_estatistico_instataneo(conn)
            df_pesquisa = get_pesquisa_por_data(conn, data_inicio, data_fim)
        finally:
            conn.close()
        
        # Retorna as duas consultas, por exemplo como um dicionário
        return {
            "ligacoes": df_ligacoes,
            "asana": df_asana,
            "online": df_online,
            "estatistico": df_estatistico,
            "pesquisa": df_pesquisa
        }
    except Exception:
        return {
            "ligacoes": pd.DataFrame(),
            "asana": pd.DataFrame(),
            "online": pd.DataFrame(),
            "estatistico": pd.DataFrame(),
            "pesquisa": pd.DataFrame()
        }

