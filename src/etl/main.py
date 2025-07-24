from datetime import datetime, timedelta
import pandas as pd

import sys
import os

# Adiciona o diretório raiz do projeto ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.api_client.client import ApiClient
from src.etl.transform import transformar_dados

def extrair_dados(client: ApiClient, endpoint: str, params=None) -> pd.DataFrame:
    

    dados_json = client.get(endpoint=endpoint, params=params)

    if not dados_json:
        print("⚠️ Nenhum dado retornado.")
        return pd.DataFrame()

    print("📦 Dados brutos recebidos da API: ", endpoint)
    return pd.DataFrame(dados_json)  

def main(client, endpoint: str, params=None)->pd.DataFrame:

    df = pd.DataFrame()

    if client.authenticate():
        print("✅ Autenticado com sucesso.")
        df_raw = extrair_dados(client, endpoint, params)

        if not df_raw.empty:

            df = transformar_dados(df_raw)
       
    else:
        print("❌ Falha na autenticação")

    return df


