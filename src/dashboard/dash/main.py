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
from src.db.connection import get_ligacoes_por_data


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

def calcula_nota(df, tipo):
# Se não encontrou, retorna vazio
    if df.empty:
        st.warning("❗ Nenhuma pergunta encontrada.")
    else:
        # 2. Explode a coluna de respostas (lista de dicionários)
        df_exploded = df.explode("respostas").reset_index(drop=True)

        # 3. Converte a coluna de dicionários em colunas reais
        df_respostas = pd.json_normalize(df_exploded["respostas"])
        
        # Junta com as outras colunas do DataFrame original
        df_respostas["nom_pergunta"] = df_exploded["nom_pergunta"].values

        # 4. Limpa os dados
        df_respostas["nota"] = pd.to_numeric(df_respostas["nom_valor"], errors="coerce")
        df_respostas["nom_agente"] = df_respostas["nom_agente"].str.strip()

        df_final = pd.DataFrame()

        # 5. Aplica pontuação
        if tipo == "csat":
            df_respostas["pontuacao"] = df_respostas["nota"].apply(classificar_csat)

            

        else:
            df_respostas["pontuacao"] = df_respostas["nota"].apply(classificar_nps)
            df_respostas = df_respostas[df_respostas["pontuacao"] != 0]

        df_final = (
                df_respostas.dropna(subset=["pontuacao", "nom_agente"])
                .groupby("nom_agente", as_index=False)["pontuacao"]
                .mean()
                .round(2)
            )
        
        return df_final



def main():
    st.set_page_config(page_title="Dashboard CRD", layout="wide")
    st.title("DASHBOARD CRD")

    setor = st.selectbox(
        "Selecione o setor:",
        ["", "NRC", "Suporte - PF", "Trafego Pago", "Acordo - N2", "Cancelamento - PF"]
    )

    # Inicializa estados
    if "last_update_kpi" not in st.session_state:
        st.session_state.last_update_kpi = datetime.min
        st.session_state.df_exibicao = pd.DataFrame()
    if "last_update_asana" not in st.session_state:
        st.session_state.last_update_asana = datetime.min
        st.session_state.df_asana = pd.DataFrame()

    client = ApiClient()

    agora = datetime.now()
    data_final = agora
    data_inicial = agora - timedelta(hours=7)

    formato = "%Y-%m-%d %H:%M:%S"
    params = {
        "data_inicial": data_inicial.strftime(formato),
        "data_final": data_final.strftime(formato),
        "agrupador": "agente"
    }

    formato_data = "%Y-%m-%d"

    params2 = {
        "data_inicial": data_inicial.strftime(formato_data),
        "data_final": data_final.strftime(formato_data), 
        "pesquisa" : 16
    }

    if setor:
        params["servico"] = setor

    tempo_kpi = (agora - st.session_state.last_update_kpi).total_seconds()
    tempo_asana = (agora - st.session_state.last_update_asana).total_seconds()

    atualiza_kpi = tempo_kpi > 14
    atualiza_asana = tempo_asana > 59

    df_ligacoes = get_ligacoes_por_data(
        data_inicial.strftime(formato),
        data_final.strftime(formato)
    )

    if not df_ligacoes.empty:
        # Classifica chamadas
        df_ligacoes["status"] = df_ligacoes["status"].str.upper()
        df_ligacoes["tipo"] = df_ligacoes["status"].apply(
            lambda x: "RECEBIDA" if "RECEB" in x else "REALIZADA"
        )

        # Agrupa por agente e tipo
        df_ligacoes_agg = (
            df_ligacoes.groupby(["agente", "tipo"])
            .size()
            .unstack(fill_value=0)
            .reset_index()
            .rename(columns={"agente": "agrupador"})
        )
    else:
        df_ligacoes_agg = pd.DataFrame()


    if atualiza_kpi:
        df_relAtEstatistico = etl_module.main(client, "relAtEstatistico", params)

        # Atualiza os dados "lentos" a cada 60 segundos
        if atualiza_asana or "df_agentesOnline" not in st.session_state:
            st.session_state.df_agentesOnline = etl_module.main(client, "agentesOnline")
            st.session_state.df_pesquisa = etl_module.main(client, "RelPesqAnalitico", params2)

            df_pesquisa = st.session_state.df_pesquisa
            st.session_state.df_csat = df_pesquisa[df_pesquisa["nom_pergunta"].str.contains("##1f449##", na=False)].copy()
            st.session_state.df_nps = df_pesquisa[df_pesquisa["nom_pergunta"].str.contains("##1f4e3##", na=False)].copy()

            st.session_state.df_csat_final = calcula_nota(st.session_state.df_csat, "csat").rename(columns={'pontuacao': '%CSAT'})
            st.session_state.df_nps_final = calcula_nota(st.session_state.df_nps, "nps").rename(columns={'pontuacao': '%NPS'})

            st.session_state.df_asana = asana_client()
            st.session_state.last_update_asana = agora

        # Recupera os dados persistidos no session_state
        df_agentesOnline = st.session_state.df_agentesOnline
        df_csat_final = st.session_state.df_csat_final
        df_nps_final = st.session_state.df_nps_final

        if not df_relAtEstatistico.empty and not df_agentesOnline.empty:
            st.session_state.last_update_kpi = agora

            # Padroniza nomes
            dataframes_renomear = [df_agentesOnline, df_csat_final, df_nps_final]
            dataframes_renomear = [df.rename(columns={'nom_agente': 'agrupador'}) for df in dataframes_renomear]
            df_agentesOnline, df_csat_final, df_nps_final = dataframes_renomear

            # Merge principal
            df_relAtEstatistico = (
                df_relAtEstatistico
                .merge(df_agentesOnline, how="inner", on="agrupador")
                .merge(df_csat_final, how="inner", on="agrupador")
                .merge(df_nps_final, how="inner", on="agrupador")
            )

            if not df_ligacoes_agg.empty:
                df_relAtEstatistico = df_relAtEstatistico.merge(df_ligacoes_agg, how="left", on="agrupador")
                df_relAtEstatistico[["RECEBIDA", "REALIZADA"]] = df_relAtEstatistico[["RECEBIDA", "REALIZADA"]].fillna(0).astype(int)
            else:
                df_relAtEstatistico["RECEBIDA"] = 0
                df_relAtEstatistico["REALIZADA"] = 0

            df = df_relAtEstatistico.copy()
            df = df[[ 
                'agrupador', 
                'dat_login',
                'tmia',
                'tma',
                'tempo_status',
                'nom_pausa',
                'tempo_logado',
                'num_qtd', 
                'tmic', 
                'status', 
                '%CSAT',
                '%NPS',
                'REALIZADA',
                'RECEBIDA'
            ]].rename(columns={
                "agrupador": "Nome",
                "num_qtd": "QTD",
                "tma": "TMA",
                "tmic": "TMIC",
                "tmia": "TMIA",
                "status": "Status",
                "dat_login": "Hora Login",
                "tempo_status": "Tempo Status",
                "nom_pausa": "Pausa",
                "tempo_logado": "Tempo Logado"
            })

            df['QTD'] = pd.to_numeric(df['QTD'], errors='coerce').fillna(0).astype(int)
            df = df.sort_values(by="TMIA", ascending=True).reset_index(drop=True)

            df["Hora Login"] = pd.to_datetime(df["Hora Login"], errors="coerce").dt.strftime('%H:%M:%S')
            df["TMIA_td"] = pd.to_timedelta(df["TMIA"])
            df["TMIA_fmt"] = df["TMIA_td"].apply(lambda x: f"{int(x.total_seconds() // 60):02}:{int(x.total_seconds() % 60):02}")
            df["TMIA_segundos"] = df["TMIA_td"].dt.total_seconds()
            df["TMIA"] = df["TMIA_fmt"]

            st.session_state.df_exibicao = df


    # --- Estilização ---
    def cor_gradiente(val):
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
        # Remove colunas auxiliares
        df = df.drop(columns=["TMIA_td", "TMIA_fmt", "TMIA_segundos"])

        # Inicializa styles vazios
        styles = pd.DataFrame('', index=df.index, columns=df.columns)

        # Aplica cor gradiente na coluna TMIA baseada no valor em segundos
        for idx, val in zip(df.index, st.session_state.df_exibicao["TMIA_segundos"]):
            styles.loc[idx, "TMIA"] = cor_gradiente(val)

        # Retorna o Styler com alinhamento, cor e formatação para %CSAT e %NPS
        return (
            df.style
            .set_properties(**{'text-align': 'center'})
            .apply(lambda _: styles, axis=None)
            .format({"%CSAT": lambda x: f"{x:.2f}".replace('.', ',')})
            .format({"%NPS": lambda x: f"{x:.2f}".replace('.', ',')})
        )


    # --- Exibição vertical ---
    st.subheader("Relatório KPI Estatístico")
    df_kpi = st.session_state.df_exibicao
    if not df_kpi.empty:
        altura = min(900, 35 + len(df_kpi) * 35)
        df_kpi = df_kpi.reset_index(drop=True)
        df_kpi.index = df_kpi.index + 1
        df_kpi.index.name = 'Rank'
        st.dataframe(estilizar(df_kpi), use_container_width=True, height=altura)
    else:
        st.info("Aguardando dados de KPI...")

    st.subheader("Relatório Asana")
    df_asana = st.session_state.df_asana
    if not df_asana.empty:
        st.dataframe(df_asana, use_container_width=True)
    else:
        st.info("Aguardando dados do Asana...")

    # --- Atualização contínua ---
    st_autorefresh(interval=15 * 1000, key="auto_refresh")


if __name__ == "__main__":
    main()
