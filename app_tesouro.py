import streamlit as st
import pandas as pd
import numpy as np

# URL do arquivo do Tesouro Direto
TESOURO_URL = "https://www.tesourotransparente.gov.br/ckan/dataset/df56aa42-484a-4a59-8184-7676580c81e3/resource/796d2059-14e9-44e3-80c9-2d9e30b405c1/download/PrecoTaxaTesouroDireto.csv"

# Título do app
st.title("Análise de Variação do Tesouro Direto")

# Carregar os dados
@st.cache_data
def load_data(url):
    try:
        data = pd.read_csv(url, sep=";", decimal=",")  # Especificando o separador decimal
        return data
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")
        return None

# Carregar o arquivo do Tesouro Direto
df = load_data(TESOURO_URL)

if df is not None:
    # Mostrar primeiras linhas para inspeção
    with st.expander("Ver primeiras linhas dos dados"):
        st.dataframe(df.head())
    
    # Garantir que as colunas necessárias existam
    required_columns = ["Data Base", "Tipo Titulo", "PU Base Manha", "Data Vencimento"]
    if all(col in df.columns for col in required_columns):
        # Converter "Data Base" e "Data Vencimento" para datetime
        df["Data Base"] = pd.to_datetime(df["Data Base"], format="%d/%m/%Y", errors='coerce')
        df["Data Vencimento"] = pd.to_datetime(df["Data Vencimento"], format="%d/%m/%Y", errors='coerce')
        
        # Remover linhas com datas inválidas
        df = df.dropna(subset=["Data Base", "Data Vencimento"])

        # Converter "PU Base Manha" para numérico (garantindo que pontos decimais sejam tratados corretamente)
        # Se os números estiverem no formato brasileiro (com vírgula como separador decimal)
        if isinstance(df["PU Base Manha"].iloc[0], str):
            df["PU Base Manha"] = df["PU Base Manha"].str.replace(',', '.').astype(float)
        else:
            df["PU Base Manha"] = pd.to_numeric(df["PU Base Manha"], errors="coerce")

        # Remover linhas com valores NaN no PU Base Manha
        df = df.dropna(subset=["PU Base Manha"])

        # Criar uma nova coluna com o ano de "Data Vencimento"
        df["Ano Vencimento"] = df["Data Vencimento"].dt.year

        # Ordenar os dados por "Data Base"
        df = df.sort_values(by="Data Base")

        # Obter os dois dias mais recentes
        recent_dates = df["Data Base"].drop_duplicates().nlargest(2).tolist()

        if len(recent_dates) == 2:
            st.write(f"Datas analisadas: {recent_dates[0].strftime('%d/%m/%Y')} e {recent_dates[1].strftime('%d/%m/%Y')}")
            
            # Criar uma coluna de agrupamento combinando "Tipo Titulo" e "Ano Vencimento"
            df["Grupo"] = df["Tipo Titulo"] + " " + df["Ano Vencimento"].astype(str)
            
            # Método alternativo para calcular a variação
            # Filtrar os dados para cada dia e mesclar
            df_recent = df[df["Data Base"].isin(recent_dates)]
            
            # Criar dataframes separados para cada data
            df_day1 = df_recent[df_recent["Data Base"] == recent_dates[0]][["Grupo", "PU Base Manha"]]
            df_day2 = df_recent[df_recent["Data Base"] == recent_dates[1]][["Grupo", "PU Base Manha"]]
            
            # Renomear colunas para evitar conflitos
            df_day1 = df_day1.rename(columns={"PU Base Manha": "PU_Recente"})
            df_day2 = df_day2.rename(columns={"PU Base Manha": "PU_Anterior"})
            
            # Mesclar os dataframes
            result_df = pd.merge(df_day1, df_day2, on="Grupo", how="inner")
            
            # Calcular a variação percentual
            result_df["Variação (%)"] = ((result_df["PU_Recente"] - result_df["PU_Anterior"]) / 
                                         result_df["PU_Anterior"]) * 100
            
            # Exibir os resultados
            st.subheader("Variação Percentual do PU Base Manhã")
            
            # Formatar o DataFrame final para exibição
            display_df = result_df[["Grupo", "PU_Anterior", "PU_Recente", "Variação (%)"]]
            display_df = display_df.rename(columns={
                "PU_Anterior": f"PU {recent_dates[1].strftime('%d/%m/%Y')}",
                "PU_Recente": f"PU {recent_dates[0].strftime('%d/%m/%Y')}"
            })
            
            # Ordenar por variação percentual (do maior para o menor)
            display_df = display_df.sort_values(by="Variação (%)", ascending=False)
            
            # Formatar a coluna de variação para mostrar 2 casas decimais
            display_df["Variação (%)"] = display_df["Variação (%)"].round(2)
            
            # Exibir o dataframe final
            st.dataframe(display_df)
            
            # Adicionar visualização gráfica
            st.subheader("Visualização Gráfica das Variações")
            chart_data = display_df.set_index("Grupo")[["Variação (%)"]]
            st.bar_chart(chart_data)
            
        else:
            st.warning("Não há dados suficientes para calcular a variação.")
    else:
        st.error(f"O arquivo deve conter as colunas: {', '.join(required_columns)}")
else:
    st.error("Não foi possível carregar os dados.")