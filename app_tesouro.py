import streamlit as st
import pandas as pd
import numpy as np

# Importa funções do api_tesouro.py
from api_tesouro import status_mercado_df, consultaTD

# URL do arquivo do Tesouro Direto
TESOURO_URL = "https://www.tesourotransparente.gov.br/ckan/dataset/df56aa42-484a-4a59-8184-7676580c81e3/resource/796d2059-14e9-44e3-80c9-2d9e30b405c1/download/PrecoTaxaTesouroDireto.csv"

# === SIDEBAR: Imagem, Status do Mercado e Taxas de Referência ===
with st.sidebar:
    st.image("tesouro_direto.jpeg", width=120, use_container_width=True)  # Removido caption
    status_df = status_mercado_df()
    status = status_df["Status"].iloc[0]
    if status.lower() == "aberto":
        color = "green"
        emoji = "🟢"
    else:
        color = "red"
        emoji = "🔴"

    # Melhor visualização: tabela com duas linhas (Abertura/Fechamento)
    status_table = pd.DataFrame([
        {
            "Evento": "Abertura",
            "Data": status_df["Data Abertura"].iloc[0],
            "Horário": status_df["Horário de Abertura"].iloc[0]
        },
        {
            "Evento": "Fechamento",
            "Data": status_df["Data Fechamento"].iloc[0],
            "Horário": status_df["Horário de Fechamento"].iloc[0]
        }
    ])

    st.markdown(
        f"### Status do Mercado\n"
        f"<span style='color:{color}; font-size: 20px'>{emoji} {status}</span>",
        unsafe_allow_html=True
    )
    st.dataframe(status_table, hide_index=True, use_container_width=True)

    st.markdown("---")
    st.markdown("#### Informe a taxa de referência para cada grupo:")
    taxa_ref_selic = st.number_input("Taxa referência SELIC (%)", min_value=0.0, max_value=100.0, value=14.0, step=0.01, format="%.2f")
    taxa_ref_prefixado = st.number_input("Taxa referência PREFIXADO (%)", min_value=0.0, max_value=100.0, value=14.0, step=0.01, format="%.2f")
    taxa_ref_ipca = st.number_input("Taxa referência IPCA (%)", min_value=0.0, max_value=100.0, value=7.0, step=0.01, format="%.2f")

# Título do app
st.title("Análise de Variação do Tesouro Direto")

# === ABAS: Mercado Agora e Comparação ===
tab1, tab2 = st.tabs(["Mercado Agora", "Comparação"])

with tab1:
    st.subheader("Mercado Agora")
    tipos = {'SELIC': 'S', 'PREFIXADO': 'P', 'IPCA': 'I'}
    taxas_ref = {'SELIC': taxa_ref_selic, 'PREFIXADO': taxa_ref_prefixado, 'IPCA': taxa_ref_ipca}
    titulos_atuais = {}
    for nome, tp in tipos.items():
        df_titulo = consultaTD('C', tp)
        if not df_titulo.empty:
            titulos_atuais[nome] = df_titulo[["Título", "Rentabilidade (Compra)", "Preço R$ (Compra)"]]
            st.write(f"**{nome}**")
            # Colorir as taxas conforme referência
            def highlight_taxa(val):
                try:
                    taxa = float(val)
                    ref = taxas_ref[nome]
                    if ref == 0.0:
                        return ''
                    if taxa > ref:
                        return 'background-color: #d4edda; color: #155724;'  # verde claro
                    elif taxa < ref:
                        return 'background-color: #f8d7da; color: #721c24;'  # vermelho claro
                    else:
                        return ''
                except:
                    return ''
            styled = titulos_atuais[nome].style.applymap(highlight_taxa, subset=["Rentabilidade (Compra)"])
            st.dataframe(styled, hide_index=True, use_container_width=True)
        else:
            st.write(f"Não há dados para {nome}.")

with tab2:
    st.subheader("Comparação")

    @st.cache_data
    def load_data(url):
        try:
            data = pd.read_csv(url, sep=";", decimal=",")
            return data
        except Exception as e:
            st.error(f"Erro ao carregar os dados: {e}")
            return None

    df = load_data(TESOURO_URL)

    if df is not None:
        required_columns = ["Data Base", "Tipo Titulo", "PU Base Manha", "Data Vencimento"]
        if all(col in df.columns for col in required_columns):
            df["Data Base"] = pd.to_datetime(df["Data Base"], format="%d/%m/%Y", errors='coerce')
            df["Data Vencimento"] = pd.to_datetime(df["Data Vencimento"], format="%d/%m/%Y", errors='coerce')
            df = df.dropna(subset=["Data Base", "Data Vencimento"])
            if isinstance(df["PU Base Manha"].iloc[0], str):
                df["PU Base Manha"] = df["PU Base Manha"].str.replace(',', '.').astype(float)
            else:
                df["PU Base Manha"] = pd.to_numeric(df["PU Base Manha"], errors="coerce")
            df = df.dropna(subset=["PU Base Manha"])
            df["Ano Vencimento"] = df["Data Vencimento"].dt.year
            df = df.sort_values(by="Data Base")
            data_recente = df["Data Base"].max()
            st.write(f"Última data de comparação: **{data_recente.strftime('%d/%m/%Y')}**")
            tipos = {'SELIC': 'SELIC', 'PREFIXADO': 'Prefixado', 'IPCA': 'IPCA'}
            for nome, df_atual in titulos_atuais.items():
                st.write(f"**Comparação {nome}**")
                comparacoes = []
                for idx, row in df_atual.iterrows():
                    filtro = (
                        (df["Tipo Titulo"].str.contains(tipos[nome], case=False)) &
                        (df["Data Base"] == data_recente)
                    )
                    df_match = df[filtro]
                    if not df_match.empty:
                        pu_csv = df_match.iloc[0]["PU Base Manha"]
                        pu_api = row["Preço R$ (Compra)"]
                        variacao = ((pu_api - pu_csv) / pu_csv) * 100
                        comparacoes.append({
                            "Título": row["Título"],
                            "PU API Agora": pu_api,
                            f"PU CSV {data_recente.strftime('%d/%m/%Y')}": pu_csv,
                            "Variação (%)": round(variacao, 2)
                        })
                if comparacoes:
                    df_comp = pd.DataFrame(comparacoes)
                    def color_variation(val):
                        if val > 0:
                            return 'background-color: #d4edda; color: #155724;'
                        elif val < 0:
                            return 'background-color: #f8d7da; color: #721c24;'
                        else:
                            return ''
                    styled_comp = df_comp.style.applymap(color_variation, subset=["Variação (%)"])
                    st.dataframe(styled_comp, hide_index=True, use_container_width=True)
                else:
                    st.write("Sem dados para comparação.")
        else:
            st.error(f"O arquivo deve conter as colunas: {', '.join(required_columns)}")
    else:
        st.error("Não foi possível carregar os dados.")