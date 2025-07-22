import pandas as pd

def transformar_dados(df: pd.DataFrame) -> pd.DataFrame:
    """Limpa e padroniza o DataFrame da API."""
    
    # Exemplo de limpeza: renomear colunas, remover nulos, ajustar tipos
    df = df.copy()
    
    # Renomeia colunas para padrão snake_case
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("-", "_")
    )

    # Remove colunas desnecessárias, se houver
    colunas_remover = [col for col in df.columns if "irrelevante" in col]
    df.drop(columns=colunas_remover, inplace=True, errors="ignore")

    # Conversão de datas, se houver colunas de tempo
    if "data_hora" in df.columns:
        df["data_hora"] = pd.to_datetime(df["data_hora"])

    # Exemplo: preencher valores ausentes
    df.fillna("", inplace=True)

    print("🛠️ Dados transformados com sucesso.")
    return df
