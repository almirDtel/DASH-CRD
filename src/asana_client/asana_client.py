import os
import sys
import pandas as pd
import asana
from asana.rest import ApiException
from dotenv import load_dotenv

def asana_client():

    # Carregar .env a partir da raiz do projeto (duas pastas acima)
    dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))
    load_dotenv(dotenv_path)

    # Variáveis de ambiente corrigidas
    access_token = os.getenv('API_ASANA_TOKEN')
    project_gid = os.getenv('API_ASANA_PROJECT_GID')


    if not access_token or not project_gid:
        print("❌ Token ou Project GID ausente no .env.")
        sys.exit(1)

    configuration = asana.Configuration()
    configuration.access_token = access_token
    api_client = asana.ApiClient(configuration)

    sections_api = asana.SectionsApi(api_client)
    tasks_api = asana.TasksApi(api_client)

    campos_personalizados = [
        "Cidade",
        "OLT",
        "STATUS",
        "Total de Clientes Afetados:",
        "IMPACTO",
        "Adicionado ao ARGOS?"
    ]

    def extrair_valor_custom_field(cf):
        return (
            cf.get("text_value") or
            cf.get("number_value") or
            (cf.get("enum_value") or {}).get("name") or
            cf.get("date_value")
        )



    dados = []
    df = pd.DataFrame()
    try:
        sections = sections_api.get_sections_for_project(project_gid, {})
        section_gid = None

        for section in sections:
            if 'OCORRÊNCIAS CLIENTES FINAIS EM ANDAMENTO' in section['name']:
                section_gid = section['gid']
                print(f"✅ Seção encontrada: {section['name']} | GID: {section_gid}")
                break

        if not section_gid:
            print("⚠️ Seção não encontrada.")
            sys.exit(1)

        opt_fields = (
            "custom_fields.name,custom_fields.text_value,"
            "custom_fields.number_value,custom_fields.enum_value.name"
        )

        tasks = tasks_api.get_tasks_for_section(
            section_gid,
            {'completed_since': 'now', 'opt_fields': opt_fields}
        )

        dados = []
        for task in tasks:
            if not task.get('completed'):
                linha = {campo: None for campo in campos_personalizados}
                for cf in task.get("custom_fields", []):
                    nome_campo = cf.get("name", "").strip()
                    if nome_campo in campos_personalizados:
                        linha[nome_campo] = extrair_valor_custom_field(cf)
                dados.append(linha)


        if dados:  # Verifica se a lista não está vazia
            df = pd.DataFrame(dados)
            df = df.sort_values(by='Total de Clientes Afetados:', ascending=False)


    except ApiException as e:
        print(f"❌ Erro ao acessar API Asana: {e}")

    print("\n📊 Tarefas encontradas:")
    print(df.columns)

    return df
