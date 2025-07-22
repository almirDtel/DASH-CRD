# main.py

from src.api_client.client import ApiClient
from datetime import datetime, timedelta

def main():
    client = ApiClient()

    if client.authenticate():
        print("✅ Autenticado com sucesso!")

        agora = datetime.now()
        data_final = agora - timedelta(minutes=10)
        data_inicial = agora - timedelta(hours=7)

        # Formato esperado pela API: "YYYY-MM-DD HH:MM:SS"
        formato = "%Y-%m-%d %H:%M:%S"

        params = {
            "data_inicial": data_inicial.strftime(formato),
            "data_final": data_final.strftime(formato),
            "agrupador": "agente",
            "servico": "Suporte - PF"
        }

        # Exemplo de chamada GET
        dados = client.get(endpoint="relAtEstatistico", params=params)
        print("📦 Resposta da API:", dados)
    else:
        print("❌ Falha na autenticação")

if __name__ == "__main__":
    main()
