import os
import mysql.connector
import pandas as pd
from mysql.connector import Error
from dotenv import load_dotenv

# Carrega o .env a partir da raiz do projeto
dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))
load_dotenv(dotenv_path)

def get_ligacoes_por_data(data_inicio, data_fim):
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )

        if conn.is_connected():
            query = """
                SELECT data_hora, agente, status 
                FROM ligacoes 
                WHERE data_hora BETWEEN %s AND %s
            """
            df = pd.read_sql(query, conn, params=[data_inicio, data_fim])
            conn.close()
            return df

    except Error as e:
        print(f"Erro ao conectar no banco: {e}")
        return pd.DataFrame()