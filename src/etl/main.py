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

def main(client, endpoint: str, params=None) -> pd.DataFrame:
    df = pd.DataFrame()

    # Tenta extrair dados diretamente
    df_raw = extrair_dados(client, endpoint, params)

    # Se a resposta for vazia ou nula, tenta autenticar e extrair de novo
    if df_raw is None or df_raw.empty:
        print("🔄 Tentando autenticar após falha na primeira tentativa de extração...")
        if client.authenticate():
            print("✅ Autenticado com sucesso.")
            df_raw = extrair_dados(client, endpoint, params)
        else:
            print("❌ Falha na autenticação")
            return df

    # Se conseguiu dados, transforma
    if df_raw is not None and not df_raw.empty:

        df = transformar_dados(df_raw)

    return df



