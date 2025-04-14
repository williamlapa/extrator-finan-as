import streamlit as st
import pandas as pd
import numpy as np
import io

# URL do arquivo do Tesouro Direto
TESOURO_URL = "https://www.tesourotransparente.gov.br/ckan/dataset/df56aa42-484a-4a59-8184-7676580c81e3/resource/796d2059-14e9-44e3-80c9-2d9e30b405c1/download/PrecoTaxaTesouroDireto.csv"

# Configuração inicial do Streamlit
st.set_page_config(page_title="Análise Tesouro Direto", layout="wide")

# Carregar os dados do tipo.csv (tabela de domínio)
@st.cache_data
def load_tipo_data():
    # Conteúdo do arquivo tipo.csv como string
    tipo_csv_content = """Titulo;Abreviatura;Tipo
Tesouro Prefixado 2006;T Prefixado 2006;Prefixado
Tesouro IPCA+ com Juros Semestrais 2009;T IPCA c JS 2009;Inflação
Tesouro IPCA+ com Juros Semestrais 2008;T IPCA c JS 2008;Inflação
Tesouro IPCA+ com Juros Semestrais 2007;T IPCA c JS 2007;Inflação
Tesouro IPCA+ com Juros Semestrais 2006;T IPCA c JS 2006;Inflação
Tesouro IPCA+ com Juros Semestrais 2010;T IPCA c JS 2010;Inflação
Tesouro IPCA+ com Juros Semestrais 2045;T IPCA c JS 2045;Inflação
Tesouro IPCA+ com Juros Semestrais 2035;T IPCA c JS 2035;Inflação
Tesouro IPCA+ com Juros Semestrais 2024;T IPCA c JS 2024;Inflação
Tesouro IPCA+ com Juros Semestrais 2015;T IPCA c JS 2015;Inflação
Tesouro IPCA+ com Juros Semestrais 2011;T IPCA c JS 2011;Inflação
Tesouro IPCA+ 2015;T IPCA 2015;Inflação
Tesouro IPCA+ 2024;T IPCA 2024;Inflação
Tesouro IGPM+ com Juros Semestrais 2017;T IGPM c JS 2017;Inflação
Tesouro IGPM+ com Juros Semestrais 2021;T IGPM c JS 2021;Inflação
Tesouro IGPM+ com Juros Semestrais 2006;T IGPM c JS 2021;Inflação
Tesouro IGPM+ com Juros Semestrais 2008;T IGPM c JS 2021;Inflação
Tesouro IGPM+ com Juros Semestrais 2011;T IGPM c JS 2021;Inflação
Tesouro IGPM+ com Juros Semestrais 2031;T IGPM c JS 2021;Inflação
Tesouro Prefixado com Juros Semestrais 2008;T Prefixado c JS 2008;Prefixado
Tesouro Prefixado com Juros Semestrais 2012;T Prefixado c JS 2012;Prefixado
Tesouro Prefixado com Juros Semestrais 2010;T Prefixado c JS 2010;Prefixado
Tesouro Selic 2010;T Selic 2010;Selic
Tesouro Selic 2009;T Selic 2009;Selic
Tesouro Selic 2008;T Selic 2008;Selic
Tesouro Selic 2007;T Selic 2007;Selic
Tesouro Prefixado 2008;T Prefixado 2008;Prefixado
Tesouro Prefixado 2007;T Prefixado 2007;Prefixado
Tesouro Prefixado 2009;T Prefixado 2009;Prefixado
Tesouro Educa+ 2045;T Educa 2045;Educa
Tesouro Educa+ 2033;T Educa 2033;Educa
Tesouro Educa+ 2032;T Educa 2032;Educa
Tesouro Educa+ 2037;T Educa 2037;Educa
Tesouro Educa+ 2036;T Educa 2036;Educa
Tesouro Educa+ 2030;T Educa 2030;Educa
Tesouro Educa+ 2038;T Educa 2038;Educa
Tesouro Educa+ 2043;T Educa 2043;Educa
Tesouro Educa+ 2041;T Educa 2041;Educa
Tesouro Educa+ 2047;T Educa 2047;Educa
Tesouro Educa+ 2034;T Educa 2034;Educa
Tesouro Educa+ 2044;T Educa 2044;Educa
Tesouro Selic 2026;T Selic 2026;Selic
Tesouro Selic 2027;T Selic 2027;Selic
Tesouro Selic 2031;T Selic 2031;Selic
Tesouro Selic 2029;T Selic 2029;Selic
Tesouro Selic 2028;T Selic 2028;Selic
Tesouro Prefixado 2027;T Prefixado 2027;Prefixado
Tesouro Prefixado 2026;T Prefixado 2026;Prefixado
Tesouro Prefixado 2029;T Prefixado 2029;Prefixado
Tesouro Prefixado 2032;T Prefixado 2032;Prefixado
Tesouro Prefixado 2031;T Prefixado 2031;Prefixado
Tesouro Prefixado 2028;T Prefixado 2028;Prefixado
Tesouro IPCA+ com Juros Semestrais 2040;T IPCA c JS 2040;Inflação
Tesouro IPCA+ com Juros Semestrais 2032;T IPCA c JS 2032;Inflação
Tesouro IPCA+ com Juros Semestrais 2060;T IPCA c JS 2060;Inflação
Tesouro IPCA+ com Juros Semestrais 2030;T IPCA c JS 2030;Inflação
Tesouro IPCA+ com Juros Semestrais 2050;T IPCA c JS 2050;Inflação
Tesouro IPCA+ com Juros Semestrais 2026;T IPCA c JS 2026;Inflação
Tesouro IPCA+ com Juros Semestrais 2055;T IPCA c JS 2055;Inflação
Tesouro IPCA+ 2050;T IPCA 2050;Inflação
Tesouro IPCA+ 2029;T IPCA 2029;Inflação
Tesouro IPCA+ 2040;T IPCA 2040;Inflação
Tesouro IPCA+ 2045;T IPCA 2045;Inflação
Tesouro IPCA+ 2035;T IPCA 2035;Inflação
Tesouro IPCA+ 2026;T IPCA 2026;Inflação
Tesouro Prefixado com Juros Semestrais 2029;T Prefixado c JS 2029;Prefixado
Tesouro Prefixado com Juros Semestrais 2033;T Prefixado c JS 2033;Prefixado
Tesouro Prefixado com Juros Semestrais 2031;T Prefixado c JS 2031;Prefixado
Tesouro Prefixado com Juros Semestrais 2035;T Prefixado c JS 2035;Prefixado
Tesouro Prefixado com Juros Semestrais 2027;T Prefixado c JS 2027;Prefixado
Tesouro Renda+ Aposentadoria Extra 2079;T Renda+ 2079;Renda
Tesouro Renda+ Aposentadoria Extra 2059;T Renda+ 2059;Renda
Tesouro Renda+ Aposentadoria Extra 2049;T Renda+ 2049;Renda
Tesouro Renda+ Aposentadoria Extra 2069;T Renda+ 2069;Renda
Tesouro Renda+ Aposentadoria Extra 2084;T Renda+ 2084;Renda
Tesouro Renda+ Aposentadoria Extra 2064;T Renda+ 2064;Renda
Tesouro Renda+ Aposentadoria Extra 2054;T Renda+ 2054;Renda
Tesouro Renda+ Aposentadoria Extra 2074;T Renda+ 2074;Renda
Tesouro Educa+ 2046;T Educa 2046;Educa
Tesouro Educa+ 2039;T Educa 2039;Educa
Tesouro Educa+ 2040;T Educa 2040;Educa
Tesouro Educa+ 2042;T Educa 2042;Educa
Tesouro Educa+ 2031;T Educa 2031;Educa
Tesouro Educa+ 2035;T Educa 2035;Educa
Tesouro Selic 2025;T Selic 2025;Selic
Tesouro Prefixado com Juros Semestrais 2017;T Prefixado c JS 2017;Prefixado
Tesouro Prefixado com Juros Semestrais 2014;T Prefixado c JS 2014;Prefixado
Tesouro Selic 2011;T Selic 2011;Selic
Tesouro Selic 2012;T Selic 2012;Selic
Tesouro Selic 2006;T Selic 2006;Selic
Tesouro Selic 2005;T Selic 2005;Selic
Tesouro Prefixado 2005;T Prefixado 2005;Prefixado
Tesouro IGPM+ com Juros Semestrais 2005;T IGPM c JS 2005;Inflação
Tesouro Prefixado 2025;T Prefixado 2025;Prefixado
Tesouro Prefixado com Juros Semestrais 2025;T Prefixado c JS 2025;Prefixado
Tesouro Selic 2024;T Selic 2024;Selic
Tesouro Prefixado 2024;T Prefixado 2024;Prefixado
Tesouro Selic 2023;T Selic 2023;Selic
Tesouro Prefixado com Juros Semestrais 2023;T Prefixado c JS 2023;Prefixado
Tesouro Prefixado 2023;T Prefixado 2023;Prefixado
Tesouro Prefixado 2022;T Prefixado 2022;Prefixado
Tesouro Selic 2021;T Selic 2021;Selic
Tesouro Prefixado 2021;T Prefixado 2021;Prefixado
Tesouro Prefixado com Juros Semestrais 2021;T Prefixado c JS 2021;Prefixado
Tesouro IPCA+ com Juros Semestrais 2020;T IPCA c JS 2020;Inflação
Tesouro Prefixado 2020;T Prefixado 2020;Prefixado
Tesouro IPCA+ 2019;T IPCA 2019;Inflação
Tesouro Prefixado 2019;T Prefixado 2019;Prefixado
Tesouro Prefixado 2018;T Prefixado 2018;Prefixado
Tesouro IPCA+ com Juros Semestrais 2017;T IPCA c JS 2017;Inflação
Tesouro Selic 2017;T Selic 2017;Selic
Tesouro Prefixado 2017;T Prefixado 2017;Prefixado
Tesouro Prefixado 2016;T Prefixado 2016;Prefixado
Tesouro Selic 2015;T Selic 2015;Selic
Tesouro Prefixado 2015;T Prefixado 2015;Prefixado
Tesouro Selic 2014;T Selic 2014;Selic
Tesouro Prefixado 2014;T Prefixado 2014;Prefixado
Tesouro IPCA+ com Juros Semestrais 2013;T IPCA c JS 2013;Inflação
Tesouro Selic 2013;T Selic 2013;Selic
Tesouro Prefixado com Juros Semestrais 2013;T Prefixado c JS 2013;Prefixado
Tesouro Prefixado 2013;T Prefixado 2013;Prefixado
Tesouro IPCA+ com Juros Semestrais 2012;T IPCA c JS 2012;Inflação
Tesouro Prefixado 2012;T Prefixado 2012;Prefixado
Tesouro Prefixado 2011;T Prefixado 2011;Prefixado
Tesouro Prefixado com Juros Semestrais 2011;T Prefixado c JS 2011;Prefixado
Tesouro Prefixado 2010;T Prefixado 2010;Prefixado"""
    
    # Converter string CSV para DataFrame
    df_tipo = pd.read_csv(io.StringIO(tipo_csv_content), sep=";")
    return df_tipo

# Carregar os dados do Tesouro Direto
@st.cache_data
def load_data(url):
    try:
        data = pd.read_csv(url, sep=";", decimal=",")  # Especificando o separador decimal
        return data
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")
        return None

# Função para mapear o tipo do título com base no nome
def extrair_tipo_titulo(titulo):
    if "Prefixado" in titulo:
        return "Prefixado"
    elif "IPCA" in titulo:
        return "Inflação"
    elif "IGPM" in titulo:
        return "Inflação"
    elif "Selic" in titulo:
        return "Selic"
    elif "Educa" in titulo:
        return "Educa"
    elif "Renda" in titulo:
        return "Renda"
    else:
        return "Outro"

# Função para encontrar a abreviatura com base no título e ano
def encontrar_abreviatura(titulo, ano, df_tipo):
    # Tenta encontrar o título completo
    titulo_completo = f"{titulo} {ano}"
    match = df_tipo[df_tipo["Titulo"] == titulo_completo]
    
    if not match.empty:
        return match["Abreviatura"].iloc[0]
    
    # Se não encontrar, extrai o tipo básico e tenta uma correspondência parcial
    tipo_base = titulo.split(" ")[0] + " " + titulo.split(" ")[1]  # Ex: "Tesouro Prefixado"
    
    for _, row in df_tipo.iterrows():
        if tipo_base in row["Titulo"] and str(ano) in row["Titulo"]:
            return row["Abreviatura"]
    
    # Se ainda não encontrar, cria uma abreviatura básica
    if "Prefixado" in titulo:
        prefix = "T Prefixado"
        if "Juros Semestrais" in titulo:
            prefix += " c JS"
        return f"{prefix} {ano}"
    elif "IPCA+" in titulo:
        prefix = "T IPCA"
        if "Juros Semestrais" in titulo:
            prefix += " c JS"
        return f"{prefix} {ano}"
    elif "IGPM+" in titulo:
        return f"T IGPM c JS {ano}"
    elif "Selic" in titulo:
        return f"T Selic {ano}"
    elif "Educa+" in titulo:
        return f"T Educa {ano}"
    elif "Renda+" in titulo:
        return f"T Renda+ {ano}"
    else:
        return f"{titulo} {ano}"

# Função para processar os dados e calcular a variação
def process_data(df, df_tipo, tipo_filter=None):
    # Garantir que as colunas necessárias existam
    required_columns = ["Data Base", "Tipo Titulo", "PU Base Manha", "Data Vencimento"]
    if all(col in df.columns for col in required_columns):
        # Converter "Data Base" e "Data Vencimento" para datetime
        df["Data Base"] = pd.to_datetime(df["Data Base"], format="%d/%m/%Y", errors='coerce')
        df["Data Vencimento"] = pd.to_datetime(df["Data Vencimento"], format="%d/%m/%Y", errors='coerce')
        
        # Remover linhas com datas inválidas
        df = df.dropna(subset=["Data Base", "Data Vencimento"])

        # Converter "PU Base Manha" para numérico
        if isinstance(df["PU Base Manha"].iloc[0], str):
            df["PU Base Manha"] = df["PU Base Manha"].str.replace(',', '.').astype(float)
        else:
            df["PU Base Manha"] = pd.to_numeric(df["PU Base Manha"], errors="coerce")

        # Remover linhas com valores NaN no PU Base Manha
        df = df.dropna(subset=["PU Base Manha"])

        # Criar uma nova coluna com o ano de "Data Vencimento"
        df["Ano Vencimento"] = df["Data Vencimento"].dt.year

        # Adicionar uma coluna de "Tipo" baseada no nome do título
        df["Tipo"] = df["Tipo Titulo"].apply(extrair_tipo_titulo)
        
        # Filtrar por tipo se especificado
        if tipo_filter and tipo_filter != "Todos":
            df = df[df["Tipo"] == tipo_filter]

        # Ordenar os dados por "Data Base"
        df = df.sort_values(by="Data Base")

        # Obter os dois dias mais recentes
        recent_dates = df["Data Base"].drop_duplicates().nlargest(2).tolist()

        if len(recent_dates) == 2 and not df.empty:
            # Criar uma coluna de agrupamento combinando "Tipo Titulo" e "Ano Vencimento"
            df["Grupo"] = df["Tipo Titulo"] + " " + df["Ano Vencimento"].astype(str)
            
            # Adicionar uma coluna de abreviatura
            df["Abreviatura"] = df.apply(lambda row: encontrar_abreviatura(row["Tipo Titulo"], row["Ano Vencimento"], df_tipo), axis=1)
            
            # Filtrar os dados para cada dia e mesclar
            df_recent = df[df["Data Base"].isin(recent_dates)]
            
            # Criar dataframes separados para cada data
            df_day1 = df_recent[df_recent["Data Base"] == recent_dates[0]][["Grupo", "Tipo Titulo", "Tipo", "Abreviatura", "PU Base Manha"]]
            df_day2 = df_recent[df_recent["Data Base"] == recent_dates[1]][["Grupo", "Tipo Titulo", "PU Base Manha"]]
            
            # Renomear colunas para evitar conflitos
            df_day1 = df_day1.rename(columns={"PU Base Manha": "PU_Recente"})
            df_day2 = df_day2.rename(columns={"PU Base Manha": "PU_Anterior"})
            
            # Mesclar os dataframes
            result_df = pd.merge(df_day1, df_day2, on=["Grupo", "Tipo Titulo"], how="inner")
            
            # Calcular a variação percentual
            result_df["Variação (%)"] = ((result_df["PU_Recente"] - result_df["PU_Anterior"]) / 
                                     result_df["PU_Anterior"]) * 100
            
            return result_df, recent_dates
    
    return None, None

# Layout principal do aplicativo
st.title("Análise de Variação do Tesouro Direto")

# Carregar os dados
df = load_data(TESOURO_URL)
df_tipo = load_tipo_data()

# Criar abas
tab1, tab2 = st.tabs(["Análise Geral", "Análise por Tipo"])

if df is not None and df_tipo is not None:
    # Aba 1: Análise Geral (sem filtros)
    with tab1:
        # Mostrar primeiras linhas para inspeção
        with st.expander("Ver primeiras linhas dos dados"):
            st.dataframe(df.head())
        
        # Processar dados sem filtro
        result_df, recent_dates = process_data(df, df_tipo)
        
        if result_df is not None:
            st.write(f"Datas analisadas: {recent_dates[0].strftime('%d/%m/%Y')} e {recent_dates[1].strftime('%d/%m/%Y')}")
            
            # Exibir os resultados
            st.subheader("Variação Percentual do PU Base Manhã")
            
            # Formatar o DataFrame final para exibição usando os nomes completos
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
    
    # Aba 2: Análise por Tipo
    with tab2:
        # Debug: Mostrar os tipos de títulos encontrados no arquivo
        df_debug = df.copy()
        df_debug["Tipo"] = df_debug["Tipo Titulo"].apply(extrair_tipo_titulo)
        tipos_encontrados = sorted(df_debug["Tipo"].unique())
        
        with st.expander("Depuração: Tipos encontrados no arquivo"):
            st.write(tipos_encontrados)
        
        # Obter lista de tipos únicos
        tipos_unicos = sorted(["Prefixado", "Inflação", "Selic", "Educa", "Renda"])
        tipos_opcoes = ["Todos"] + tipos_unicos
        
        # Seletor de tipo
        tipo_selecionado = st.selectbox("Selecione o tipo de título:", tipos_opcoes)
        
        # Processar dados com filtro
        result_df, recent_dates = process_data(df, df_tipo, tipo_selecionado if tipo_selecionado != "Todos" else None)
        
        if result_df is not None:
            st.write(f"Datas analisadas: {recent_dates[0].strftime('%d/%m/%Y')} e {recent_dates[1].strftime('%d/%m/%Y')}")
            
            # Exibir os resultados com abreviaturas
            st.subheader("Variação Percentual do PU Base Manhã")
            
            # Formatar o DataFrame para exibição
            display_df = result_df[["Abreviatura", "Tipo", "PU_Anterior", "PU_Recente", "Variação (%)"]]
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
            
            # Adicionar visualização gráfica usando as abreviaturas
            st.subheader("Visualização Gráfica das Variações")
            chart_data = display_df.set_index("Abreviatura")[["Variação (%)"]]
            st.bar_chart(chart_data)
        else:
            st.warning("Não há dados suficientes para calcular a variação ou não existem títulos deste tipo.")
else:
    st.error("Não foi possível carregar os dados necessários.")