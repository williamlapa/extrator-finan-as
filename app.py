import streamlit as st
import pandas as pd
import requests
import os

# Configurações
TESOURO_URL = "https://www.tesourotransparente.gov.br/ckan/dataset/df56aa42-484a-4a59-8184-7676580c81e3/resource/796d2059-14e9-44e3-80c9-2d9e30b405c1/download/PrecoTaxaTesouroDireto.csv"
TIPO_FILE_PATH = "tipo.xlsx"  # Caminho da planilha tipo.xlsx

# Função para baixar e carregar os dados do Tesouro
@st.cache_data
def carregar_dados_tesouro(url):
    try:
        resposta = requests.get(url)
        resposta.raise_for_status()
        with open("PrecoTaxaTesouroDireto.csv", "wb") as file:
            file.write(resposta.content)
        df = pd.read_csv("PrecoTaxaTesouroDireto.csv", sep=";", encoding="latin1")
        
        # Criar a coluna "Titulo" concatenando "Tipo Titulo" com o ano de "Data Vencimento"
        df["Data Vencimento"] = pd.to_datetime(df["Data Vencimento"], dayfirst=True, errors="coerce")
        df["Titulo"] = df["Tipo Titulo"] + " " + df["Data Vencimento"].dt.year.astype(str)
        
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados do Tesouro: {e}")
        return None

# Função para carregar a planilha tipo.xlsx
@st.cache_data
def carregar_planilha_tipo(caminho):
    try:
        return pd.read_excel(caminho)
    except Exception as e:
        st.error(f"Erro ao carregar a planilha tipo.xlsx: {e}")
        return None

# Função para calcular a variação percentual entre os dias mais recentes usando PU Base Manha
def calcular_variacao(df_tesouro, df_tipo):
    try:
        # Remover espaços extras e normalizar para maiúsculas
        df_tesouro["Titulo"] = df_tesouro["Titulo"].str.strip().str.upper()
        df_tipo["Titulo"] = df_tipo["Titulo"].str.strip().str.upper()

        # Exibir valores únicos para depuração
        st.write("Valores únicos em df_tesouro['Titulo']:", df_tesouro["Titulo"].unique())
        st.write("Valores únicos em df_tipo['Titulo']:", df_tipo["Titulo"].unique())

        # Cruzar os dados do Tesouro com a planilha tipo.xlsx usando a coluna "Titulo"
        df_cruzado = pd.merge(df_tesouro, df_tipo, on="Titulo", how="inner")

        # Verificar se o cruzamento resultou em dados
        if df_cruzado.empty:
            st.warning("O cruzamento resultou em um DataFrame vazio. Verifique os valores das colunas 'Titulo'.")
            return None

        # Converter a coluna "Data Base" para datetime
        df_cruzado["Data Base"] = pd.to_datetime(df_cruzado["Data Base"], dayfirst=True, errors="coerce")
        
        # Ordenar os dados pela data mais recente
        df_cruzado = df_cruzado.sort_values(by=["Data Base"], ascending=False)
        
        # Converter a coluna "PU Base Manha" para numérico
        df_cruzado["PU Base Manha"] = pd.to_numeric(df_cruzado["PU Base Manha"], errors="coerce")
        
        # Calcular a diferença entre os dias mais recentes
        df_cruzado["Variação"] = df_cruzado.groupby("Titulo")["PU Base Manha"].diff(-1)
        
        # Calcular a variação percentual
        df_cruzado["Variação (%)"] = (df_cruzado["Variação"] / df_cruzado["PU Base Manha"].shift(-1)) * 100
        
        return df_cruzado
    except Exception as e:
        st.error(f"Erro ao calcular variação: {e}")
        return None

# Função principal
def main():
    st.title("📊 Análise de Dados do Tesouro Direto")

    # Carregar dados do Tesouro
    st.subheader("Dados do Tesouro Direto")
    df_tesouro = carregar_dados_tesouro(TESOURO_URL)
    if df_tesouro is not None:
        st.write("Dados carregados com sucesso!")
        st.write("Colunas do Tesouro:", df_tesouro.columns.tolist())  # Verificar nomes das colunas
        st.dataframe(df_tesouro.head())

    # Carregar planilha tipo.xlsx
    st.subheader("Dados da Planilha tipo.xlsx")
    df_tipo = carregar_planilha_tipo(TIPO_FILE_PATH)
    if df_tipo is not None:
        st.write("Planilha carregada com sucesso!")
        st.write("Colunas da Planilha Tipo:", df_tipo.columns.tolist())  # Verificar nomes das colunas
        st.dataframe(df_tipo.head())

    # Calcular variação após cruzamento
    if df_tesouro is not None and df_tipo is not None:
        st.subheader("Cruzamento e Variação dos Títulos")
        
        # Verifique os nomes das colunas antes do cruzamento
        if "Titulo" in df_tesouro.columns and "Titulo" in df_tipo.columns:
            st.write("Valores únicos em df_tesouro['Titulo']:", df_tesouro["Titulo"].unique())
            st.write("Valores únicos em df_tipo['Titulo']:", df_tipo["Titulo"].unique())
            
            # Remover espaços em branco das colunas "Titulo"
            df_tesouro["Titulo"] = df_tesouro["Titulo"].str.strip()
            df_tipo["Titulo"] = df_tipo["Titulo"].str.strip()
            
            df_cruzado = calcular_variacao(df_tesouro, df_tipo)
            if df_cruzado is not None:
                # Mostrar apenas Titulo e Variação (%)
                st.dataframe(df_cruzado[["Titulo", "Variação (%)"]].dropna().head())
        else:
            st.error("A coluna 'Titulo' não foi encontrada nos DataFrames.")

if __name__ == "__main__":
    main()