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
        
        # Converter a coluna "Data Vencimento" para datetime
        df["Data Vencimento"] = pd.to_datetime(df["Data Vencimento"], dayfirst=True, errors="coerce")
        
        # Criar a coluna "Titulo" no formato "Tesouro [Tipo Titulo] [Ano]"
        # Este formato deve corresponder ao formato na planilha tipo.xlsx
        df["Ano"] = df["Data Vencimento"].dt.year
        
        # Mapeamento de tipos conforme aparecem na planilha tipo
        mapeamento_tipos = {
            "Tesouro Prefixado": "Tesouro Prefixado",
            "Tesouro Prefixado com Juros Semestrais": "Tesouro Prefixado com Juros Semestrais",
            "Tesouro IPCA+": "Tesouro IPCA+",
            "Tesouro IPCA+ com Juros Semestrais": "Tesouro IPCA+ com Juros Semestrais",
            "Tesouro Selic": "Tesouro Selic",
            "Tesouro IGPM+ com Juros Semestrais": "Tesouro IGPM+ com Juros Semestrais",
            "Tesouro Renda+ Aposentadoria Extra": "Tesouro Renda+ Aposentadoria Extra",
            "Tesouro Educa+": "Tesouro Educa+"
        }
        
        # Aplicar o mapeamento
        df["Tipo Normalizado"] = df["Tipo Titulo"].map(mapeamento_tipos)
        
        # Criar coluna "Titulo" no formato que corresponde à planilha tipo
        df["Titulo"] = df["Tipo Normalizado"] + " " + df["Ano"].astype(str)
        
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados do Tesouro: {e}")
        return None

# Função para carregar a planilha tipo.xlsx
@st.cache_data
def carregar_planilha_tipo(caminho):
    try:
        # Verificar se o arquivo existe
        if not os.path.exists(caminho):
            st.error(f"Arquivo {caminho} não encontrado.")
            # Criar um DataFrame temporário com os dados fornecidos
            dados = [linha.strip().split('\t') for linha in open("dados_tipo.txt", "r").readlines()]
            colunas = dados[0]
            df = pd.DataFrame(dados[1:], columns=colunas)
            return df
        
        # Se o arquivo existe, carregar normalmente
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
        st.write("Amostra de títulos no df_tesouro:", df_tesouro["Titulo"].unique()[:5])
        st.write("Amostra de títulos no df_tipo:", df_tipo["Titulo"].unique()[:5])
        
        # Verificar contagens de títulos
        st.write(f"Número de títulos únicos no df_tesouro: {len(df_tesouro['Titulo'].unique())}")
        st.write(f"Número de títulos únicos no df_tipo: {len(df_tipo['Titulo'].unique())}")
        
        # Verificar se há interseção entre os conjuntos de títulos
        titulos_tesouro = set(df_tesouro["Titulo"].unique())
        titulos_tipo = set(df_tipo["Titulo"].unique())
        intersecao = titulos_tesouro.intersection(titulos_tipo)
        st.write(f"Número de títulos em comum: {len(intersecao)}")
        if len(intersecao) > 0:
            st.write("Alguns títulos em comum:", list(intersecao)[:5])
        
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
    
    # Salvar os dados da planilha fornecida em um arquivo temporário
    with open("dados_tipo.txt", "w") as f:
        f.write("Titulo\tAbrev\tTipo\n")
        for linha in st.session_state.get("dados_tipo", []):
            f.write(linha + "\n")
    
    # Carregar dados do Tesouro
    st.subheader("Dados do Tesouro Direto")
    df_tesouro = carregar_dados_tesouro(TESOURO_URL)
    if df_tesouro is not None:
        st.write("Dados carregados com sucesso!")
        st.write("Número de registros:", len(df_tesouro))
        st.write("Colunas do Tesouro:", df_tesouro.columns.tolist())
        st.dataframe(df_tesouro.head())
    
    # Carregar planilha tipo.xlsx
    st.subheader("Dados da Planilha tipo.xlsx")
    df_tipo = carregar_planilha_tipo(TIPO_FILE_PATH)
    if df_tipo is not None:
        st.write("Planilha carregada com sucesso!")
        st.write("Número de registros:", len(df_tipo))
        st.write("Colunas da Planilha Tipo:", df_tipo.columns.tolist())
        st.dataframe(df_tipo.head())
    
    # Calcular variação após cruzamento
    if df_tesouro is not None and df_tipo is not None:
        st.subheader("Cruzamento e Variação dos Títulos")
        
        # Verificar os nomes das colunas antes do cruzamento
        if "Titulo" in df_tesouro.columns and "Titulo" in df_tipo.columns:
            df_cruzado = calcular_variacao(df_tesouro, df_tipo)
            if df_cruzado is not None:
                # Mostrar apenas Titulo e Variação (%)
                st.dataframe(df_cruzado[["Titulo", "Variação (%)"]].dropna().head(10))
                
                # Mostrar estatísticas da variação
                st.subheader("Estatísticas da Variação (%)")
                var_stats = df_cruzado["Variação (%)"].describe()
                st.write(var_stats)
                
                # Adicionar um gráfico de barras com as variações
                st.subheader("Gráfico de Variação dos Títulos")
                chart_data = df_cruzado[["Titulo", "Variação (%)"]].dropna().head(10)
                st.bar_chart(chart_data.set_index("Titulo"))
        else:
            st.error("A coluna 'Titulo' não foi encontrada nos DataFrames.")

# Inicializar dados da planilha tipo (do documento fornecido)
if "dados_tipo" not in st.session_state:
    st.session_state.dados_tipo = [
        "Tesouro Prefixado 2006\tT Prefixado 2006\tPrefixado",
        "Tesouro IPCA+ com Juros Semestrais 2009\tT IPCA c JS 2009\tInflação",
        # Adicione todas as linhas da planilha tipo aqui
    ]

if __name__ == "__main__":
    main()