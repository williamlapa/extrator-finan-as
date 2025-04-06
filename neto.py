from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2.service_account import Credentials
import io
import os

def baixar_planilha_google(drive_file_id, diretorio, nome_arquivo, credenciais_json):
    try:
        # Autenticação com a API do Google
        creds = Credentials.from_service_account_file(credenciais_json)
        service = build('drive', 'v3', credentials=creds)

        # Solicita o arquivo na API do Google Drive no formato Excel
        request = service.files().export_media(fileId=drive_file_id, mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        fh = io.BytesIO()

        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()

        # Define o caminho completo do arquivo onde será salvo
        caminho_arquivo = os.path.join(diretorio, nome_arquivo)

        # Escreve o conteúdo baixado no arquivo
        with open(caminho_arquivo, 'wb') as f:
            f.write(fh.getvalue())

        print(f"Arquivo salvo com sucesso em: {caminho_arquivo}")

    except Exception as e:
        print(f"Erro ao baixar ou salvar a planilha: {e}")


# ID do arquivo no Google Drive (extraído do link fornecido)
drive_file_id = "1gdRPlkLjaM7y6MmOBzebqqGpzxZBWztyY36iRXgX1LY"

# Diretório onde o arquivo será salvo
diretorio = r"C:\Users\willi\Downloads"

# Nome do arquivo que será salvo
nome_arquivo = "planilha_neto.xlsx"

# Caminho para o arquivo JSON de credenciais da API Google Drive
credenciais_json = r"credentials.json"

# Chama a função para baixar e salvar o arquivo
baixar_planilha_google(drive_file_id, diretorio, nome_arquivo, credenciais_json)