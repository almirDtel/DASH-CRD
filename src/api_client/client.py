import requests
from typing import Optional, Dict, Any

import sys
import os

# Adiciona o diretório raiz do projeto ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.utils.config import (
    API_BASE_URL,
    API_USERNAME,
    API_PASSWORD
)


class ApiClient:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.token: Optional[str] = None
        self.session = requests.Session()

    def authenticate(self) -> bool:
        """Realiza login e armazena o token de autenticação."""
        payload = {
            "login": API_USERNAME,
            "chave": API_PASSWORD
        }

        headers = {
            "accept": "application/json",
            "Content-Type": "application/json"
        }

        API_LOGIN_URL = f"{self.base_url}/authuser"

        try:
            response = self.session.post(API_LOGIN_URL, json=payload, headers=headers)
            response.raise_for_status()

            # DEBUG: Status e conteúdo da resposta
            print("📨 Resposta da autenticação:", response.status_code)

            try:
                json_data = response.json()
                print("📦 Conteúdo da resposta JSON:", json_data)
            except ValueError:
                print("❌ Erro ao interpretar a resposta como JSON.")
                return False

            # Verifica se a resposta é um dicionário
            if not isinstance(json_data, dict):
                print("⚠️ Resposta inesperada da API (esperado dict, recebido:", type(json_data), ")")
                return False

            result = json_data.get("result", {})
            if not isinstance(result, dict):
                print("⚠️ 'result' não é um dicionário:", result)
                return False

            self.token = result.get("token")
            if not self.token:
                print("⚠️ Token não encontrado na resposta:", json_data)
                return False

            return True

        except requests.RequestException as e:
            print(f"❌ Erro ao autenticar: {e}")
            print("API LOGIN URL:", API_LOGIN_URL)
            print("API USERNAME:", API_USERNAME)
            print("API PASSWORD:", API_PASSWORD)
            print("API_BASE_URL:", self.base_url)
            return False



    def _get_headers(self) -> Dict[str, str]:
        """Retorna os headers com o token JWT."""
        if not self.token:
            raise ValueError("Token ausente. Autenticação não realizada.")
        return {
            "accept": "application/json",
            "Authorization": f"Bearer {self.token}"
        }

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Faz requisição GET autenticada."""
        if not self.token:
            if not self.authenticate():
                return None

        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()

        try:
            response = self.session.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"❌ Erro na requisição GET: {e}")
            return None

