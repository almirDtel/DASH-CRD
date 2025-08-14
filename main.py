import json
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
        formato_data = "%Y-%m-%d"

        params = {
            "data_inicial": data_inicial.strftime(formato_data),
            "data_final": data_final.strftime(formato_data), 
            "pesquisa" : 16
        }

        # Exemplo de chamada GET
        dados = client.get(endpoint="RelPesqAnalitico", params=params)
        print("📦 Resposta da API:", dados)

        with open("resposta_api.json", "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=4)

        print("✅ Dados salvos em 'resposta_api.json'")


    else:
        print("❌ Falha na autenticação")

if __name__ == "__main__":
    main()
