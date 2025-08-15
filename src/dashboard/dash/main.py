import sys
import os
import time
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh


# Importações
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from src.etl import main as etl_module
from src.api_client.client import ApiClient
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from asana_client.asana_client import asana_client
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from src.db.connection import get_db


def classificar_csat(nota):
    if nota <= 7:
        return 0
    elif nota >= 8:
        return 100
    return None

def classificar_nps(nota):
    if nota <= 6:
        return -100
    elif nota <= 8:
        return 0
    elif nota >=9:
        return 100
    return None

def calcula_nota_df(df, tipo):
    if df.empty:
        return pd.DataFrame(columns=["agente", "pontuacao"])
    
    # Limpa os dados
    df["nota"] = pd.to_numeric(df["nom_valor"], errors="coerce")
    df["agente"] = df["agente"].str.strip()

    # Aplica pontuação
    if tipo.lower() == "csat":
        df["pontuacao"] = df["nota"].apply(classificar_csat)
    else:
        df["pontuacao"] = df["nota"].apply(classificar_nps)
        df = df[df["pontuacao"] != 0]

    # Agrupa por agente
    df_final = (
        df.dropna(subset=["pontuacao", "agente"])
        .groupby("agente", as_index=False)["pontuacao"]
        .mean()
        .round(2)
    )
    return df_final

def main():
    st.set_page_config(page_title="Dashboard CRD", layout="wide")
    st.title("DASHBOARD CRD")
    df = pd.DataFrame()

    # --- Filtro de setor com selectbox persistente ---
    setores = ["", "NRC", "Suporte - PF", "Trafego Pago", "Acordo - N2", "Cancelamento - PF"]

    if "setor" not in st.session_state:
        st.session_state.setor = ""

    setor = st.selectbox(
        "Selecione o setor:",
        setores,
        index=setores.index(st.session_state.setor)
    )

    if setor != st.session_state.setor:
        st.session_state.setor = setor
        st.rerun()

    setor = st.session_state.setor

    # --- Datas ---
    agora = datetime.now()
    data_final = agora
    data_inicial = agora - timedelta(hours=7)
    formato = "%Y-%m-%d %H:%M:%S"

    # --- Dados do banco ---
    dados_database = get_db(data_inicial.strftime(formato), data_final.strftime(formato))
    df_ligacoes = dados_database["ligacoes"]

    if not df_ligacoes.empty:
        df_ligacoes["status"] = df_ligacoes["status"].str.upper()
        df_ligacoes["tipo"] = df_ligacoes["status"].apply(
            lambda x: "RECEBIDA" if "RECEB" in x else "REALIZADA"
        )
        df_ligacoes_agg = (
            df_ligacoes.groupby(["agente", "tipo"])
            .size()
            .unstack(fill_value=0)
            .reset_index()
        )
    else:
        df_ligacoes_agg = pd.DataFrame()

    df_relAtEstatistico = dados_database["estatistico"]
    df_agentesOnline = dados_database["online"]
    df_pesquisa = dados_database["pesquisa"]

    df_csat = df_pesquisa[df_pesquisa["nom_pergunta"].str.contains("##1f449##", na=False)].drop(columns=["nom_pergunta"])

    df_nps = df_pesquisa[df_pesquisa["nom_pergunta"].str.contains("##1f4e3##", na=False)].drop(columns=["nom_pergunta"])

    # Calcula as notas
    df_csat_final = calcula_nota_df(df_csat, "csat")
    df_nps_final  = calcula_nota_df(df_nps, "nps")

    # Junta em um único DataFrame
    df_resultado = pd.merge(df_csat_final, df_nps_final, on="agente", how="outer", suffixes=("_csat", "_nps"))

    if not df_relAtEstatistico.empty and not df_agentesOnline.empty:
        df_relAtEstatistico = df_relAtEstatistico.merge(df_agentesOnline, how="inner", on="agente")

        if not df_ligacoes_agg.empty:
            df_relAtEstatistico = df_relAtEstatistico.merge(df_ligacoes_agg, how="left", on="agente")
            for col in ["RECEBIDA", "REALIZADA"]:
                if col not in df_relAtEstatistico.columns:
                    df_relAtEstatistico[col] = 0
            df_relAtEstatistico[["RECEBIDA", "REALIZADA"]] = (
                df_relAtEstatistico[["RECEBIDA", "REALIZADA"]].fillna(0).astype(int)
            )
        else:
            df_relAtEstatistico["RECEBIDA"] = 0
            df_relAtEstatistico["REALIZADA"] = 0

        if not df_resultado.empty:
            df_relAtEstatistico = df_relAtEstatistico.merge(df_resultado, how="left", on="agente")

        df = df_relAtEstatistico.copy()

        # --- Filtro pelo setor ---
        if setor:
            df = df[df["servico"] == setor]

        df = df[[
            'agente', 'servico', 'pontuacao_csat', 'tmia', 'tma', 'tempo_status', 'status',
            'pausa', 'dat_login', 'tempo_logado', 'num_qtd', 'RECEBIDA', 'REALIZADA', 'pontuacao_nps'
        ]].rename(columns={
            "agente": "Nome",
            "num_qtd": "💬 QTD",
            "tma": "TMA",
            "tmia": "TMIA",
            "status": "Status",
            "dat_login": "Hora Login",
            "tempo_status": "Tempo Status",
            "pausa": "Pausa",
            "tempo_logado": "Tempo Logado",
            'RECEBIDA':'📞 ↙️', 
            'REALIZADA': '📞 ⬈',
            'pontuacao_csat': '%CSAT',
            'pontuacao_nps': "%NPS"
        })

        df['💬 QTD'] = pd.to_numeric(df['💬 QTD'], errors='coerce').fillna(0).astype(int)
        df = df.sort_values(by="TMIA", ascending=True).reset_index(drop=True)
        df["Hora Login"] = pd.to_datetime(df["Hora Login"], errors="coerce").dt.strftime('%H:%M:%S')
        df["TMIA_td"] = pd.to_timedelta(df["TMIA"])
        df["TMIA_fmt"] = df["TMIA_td"].apply(lambda x: f"{int(x.total_seconds() // 60):02}:{int(x.total_seconds() % 60):02}")
        df["TMIA_segundos"] = df["TMIA_td"].dt.total_seconds()
        df["TMIA"] = df["TMIA_fmt"]
        df["TMA"] = pd.to_timedelta(df["TMA"])
        df["Tempo Status"] = pd.to_timedelta(df["Tempo Status"])
        df["Tempo Logado"] = pd.to_timedelta(df["Tempo Logado"])
        df["TMA"] = df["TMA"].apply(lambda x: f"{int(x.total_seconds() // 60):02d}:{int(x.total_seconds() % 60):02d}")
        df["Tempo Status"] = df["Tempo Status"].apply(lambda x: str(x).split()[2] if "days" in str(x) else str(x))
        df["Tempo Logado"] = df["Tempo Logado"].apply(lambda x: str(x).split()[2] if "days" in str(x) else str(x))
        df['%CSAT'] = df['%CSAT'].astype(float).map("{:.2f}".format)
        df['%NPS'] = df['%NPS'].astype(float).map("{:.2f}".format)


    def cor_gradiente_tmia(val):
        if val <= 50:
            r, g, b = 0, 255, 0
        elif 50 < val <= 90:
            pct = (val - 50) / 40
            r = int(pct * 255)
            g = 255
            b = 0
        elif 90 < val <= 120:
            pct = (val - 90) / 30
            r = 255
            g = int(255 - pct * 255)
            b = 0
        elif 120 < val <= 180:
            pct = (val - 120) / 60
            r = int(255 - pct * 127)
            g = 0
            b = int(pct * 64)
        else:
            r, g, b = 128, 0, 64
        return f'background-color: rgb({r}, {g}, {b})'

    def estilizar(df):
        tmia_segundos = df["TMIA_segundos"].copy() #faz uma copia da coluna especifica para poder excluir ela do principal
        df = df.drop(columns=["TMIA_td", "TMIA_fmt", "TMIA_segundos"])  # já remove aqui
        styles = pd.DataFrame('', index=df.index, columns=df.columns)  # agora tem o shape correto
        for idx, val in zip(df.index, tmia_segundos):
            styles.loc[idx, "TMIA"] = cor_gradiente_tmia(val)
        return df.style.set_properties(**{'text-align': 'center'}).apply(lambda _: styles, axis=None)


    # --- Exibição KPI ---
    st.subheader("Relatório KPI Estatístico")
    if not df.empty:
        altura = min(900, 35 + len(df) * 35)
        df = df.reset_index(drop=True)
        df.index = df.index + 1
        df.index.name = 'Rank'
        st.dataframe(estilizar(df), use_container_width=True, height=altura)
    else:
        st.info("Aguardando dados de KPI...")


    # --- Relatório Asana ---
    st.subheader("Relatório Asana")
    df_asana = dados_database["asana"]
    if not df_asana.empty:
        st.dataframe(df_asana, use_container_width=True)
    else:
        st.info("Nenhuma emergência no Asana no momento")


    # --- Atualização contínua ---
    st_autorefresh(interval=30 * 1000, key="auto_refresh")
