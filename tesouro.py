import requests
import os
import streamlit as st

def baixar_csv(url, diretorio, nome_arquivo):
    try:
        # Fazendo o download do arquivo
        resposta = requests.get(url)
        resposta.raise_for_status()  # Verifica se ocorreu algum erro na requisição
        
        # Cria o caminho completo para salvar o arquivo
        caminho_arquivo = os.path.join(diretorio, nome_arquivo)
        
        # Salvando o arquivo no diretório especificado
        with open(caminho_arquivo, 'wb') as arquivo:
            arquivo.write(resposta.content)
        
        print(f"Arquivo salvo com sucesso em: {caminho_arquivo}")
        # Mostrando mensagem de sucesso para o usuário
        st.success(f"✅ Arquivo salvo com sucesso em:\n{caminho_arquivo}")
    
    except requests.exceptions.RequestException as e:
        print(f"Erro ao fazer o download do arquivo: {e}")
        st.error(f"Erro ao fazer o download do arquivo: {e}")
    except Exception as e:
        print(f"Erro ao salvar o arquivo: {e}")
        st.error(f"Erro ao salvar o arquivo: {e}")

# Streamlit interface
st.title('Exportador de dados do Tesouro Direto')

# URL do arquivo CSV
url = "https://www.tesourotransparente.gov.br/ckan/dataset/df56aa-484a-4a59-8184-7676580c81e3/resource/796d2059-14e9-44e3-80c9-2d9e30b405c1/download/PrecoTaxaTesouroDireto.csv"

# Nome do arquivo que será salvo
nome_arquivo = "PrecoTaxaTesouroDireto.csv"

# Usar a entrada de texto do Streamlit para o diretório
diretorio = st.text_input('Informe o diretório para salvar o arquivo CSV')

# Definir diretório padrão se não informado
if not diretorio:
    diretorio = r"C:\Users\willi\OneDrive\Documentos\Investimentos"

if st.button('Salvar CSV'):
    # Chama a função para salvar o arquivo
    baixar_csv(url, diretorio, nome_arquivo)