import sys
import os
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta




def main():
    st.title("DASHBOARD CRD")

    setor = st.selectbox(
    "Selecione o setor:",
    ["","NRC", "Suporte - PF", "Trafego Pago", "Acordo - N2", "Cancelamento - PF"])

    

    # Adiciona o diretório raiz do projeto ao sys.path
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
    from src.etl import main as etl_module
    from src.api_client.client import ApiClient


    client = ApiClient()

    agora = datetime.now()
    data_final = agora 
    data_inicial = agora - timedelta(hours=7)

    formato = "%Y-%m-%d %H:%M:%S"
    params = {
        "data_inicial": data_inicial.strftime(formato),
        "data_final": data_final.strftime(formato),
        "agrupador": "agente",
        "servico": setor
    }

    df_relAtEstatistico = pd.DataFrame()
    df_agentesOnline = pd.DataFrame()

    df_relAtEstatistico = etl_module.main(client, "relAtEstatistico", params)
    df_agentesOnline = etl_module.main(client, "agentesOnline")



    if not df_relAtEstatistico.empty and not df_agentesOnline.empty:
        df_agentesOnline = df_agentesOnline.rename(columns={'nom_agente': 'agrupador'})

        df_relAtEstatistico = df_relAtEstatistico.merge(df_agentesOnline, how="inner", on="agrupador")

        df_exibicao = df_relAtEstatistico.copy()
        df_exibicao = df_exibicao[[
            'agrupador', 
            'dat_login',
            'tmia',
            'tma',
            'tempo_status',
            'nom_pausa',
            'tempo_logado',
            'num_qtd', 
            'tmic', 
            'status'
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

        # converte a coluna 'QTD' para int
        df_exibicao['QTD'] = pd.to_numeric(df_exibicao['QTD'], errors='coerce').fillna(0).astype(int)

        df_exibicao = df_exibicao.sort_values(by="TMIA", ascending=True).reset_index(drop=True)

        # Garantir que 'Hora Login' está no formato datetime
        df_exibicao["Hora Login"] = pd.to_datetime(df_exibicao["Hora Login"], errors="coerce")

        # Formatar para mostrar apenas a hora (HH:MM:SS)
        df_exibicao["Hora Login"] = df_exibicao["Hora Login"].dt.strftime('%H:%M:%S')


        st.subheader("Relatório KPI Estatístico")
        
        # 1. Converter a coluna TMIA para timedelta
        df_exibicao["TMIA_td"] = pd.to_timedelta(df_exibicao["TMIA"])

        # 2. Criar coluna formatada como MM:SS
        df_exibicao["TMIA_fmt"] = df_exibicao["TMIA_td"].apply(lambda x: f"{int(x.total_seconds() // 60):02}:{int(x.total_seconds() % 60):02}")

        # 3. Segundos totais para usar no gradiente
        df_exibicao["TMIA_segundos"] = df_exibicao["TMIA_td"].dt.total_seconds()

        # 4. Substituir a coluna 'TMIA' pela formatada
        df_exibicao["TMIA"] = df_exibicao["TMIA_fmt"]

        # 5. Função de cor gradiente
        def cor_gradiente(val):
            if val <= 50:
                # Verde claro (fixo)
                r, g, b = 0, 255, 0
            elif 50 < val <= 90:
                # Verde → Amarelo
                pct = (val - 50) / 40  # 0 a 1
                r = int(pct * 255)
                g = 255
                b = 0
            elif 90 < val <= 120:
                # Amarelo → Vermelho
                pct = (val - 90) / 30
                r = 255
                g = int(255 - pct * 255)
                b = 0
            elif 120 < val <= 180:
                # Vermelho → Roxo escuro (bordô)
                pct = (val - 120) / 60
                r = int(255 - pct * 127)      # 255 → 128
                g = 0
                b = int(pct * 64)             # 0 → 64
            else:
                # Muito acima de 3 min (bordô escuro fixo)
                r, g, b = 128, 0, 64

            return f'background-color: rgb({r}, {g}, {b})'


        # 6. Aplicar estilo apenas à coluna TMIA
        def estilizar(df):
            # Esconder colunas auxiliares antes de estilizar
            df = df.drop(columns=["TMIA_td", "TMIA_fmt", "TMIA_segundos"])
            
            # Preparar styles só com colunas que ainda existem
            styles = pd.DataFrame('', index=df.index, columns=df.columns)

            for i, val in enumerate(df_exibicao.loc[df.index, "TMIA_segundos"]):
                styles.loc[i, "TMIA"] = cor_gradiente(val)

            return df.style.set_properties(**{'text-align': 'center'}).apply(lambda _: styles, axis=None)

        # 7. Exibir com Streamlit
        st.dataframe(estilizar(df_exibicao), use_container_width=True)


if __name__ == "__main__":
    main()