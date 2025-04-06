import streamlit as st
import pandas as pd
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv
import requests

# Carrega variáveis do .env
load_dotenv()

# Configurações de e-mail (lê do .env)
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))

# Configurações de diretórios
DOWNLOAD_FOLDER = os.getenv("download_folder")
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Configurações do Neto
NETO_SHEET_ID = os.getenv("sheet_id")
NETO_SHEET_NAME = os.getenv("sheet_name")
NETO_FILE_NAME = os.getenv("file_name")
NETO_FILE_PATH = os.path.join(DOWNLOAD_FOLDER, NETO_FILE_NAME)

# Configurações do Tesouro
TESOURO_URL = "https://www.tesourotransparente.gov.br/ckan/dataset/df56aa-484a-4a59-8184-7676580c81e3/resource/796d2059-14e9-44e3-80c9-2d9e30b405c1/download/PrecoTaxaTesouroDireto.csv"
TESOURO_FILE_NAME = "PrecoTaxaTesouroDireto.csv"
TESOURO_FILE_PATH = os.path.join(DOWNLOAD_FOLDER, TESOURO_FILE_NAME)

# Função para download da planilha do Neto
def download_spreadsheet():
    try:
        url = f"https://docs.google.com/spreadsheets/d/{NETO_SHEET_ID}/gviz/tq?tqx=out:csv&sheet={NETO_SHEET_NAME}"
        df = pd.read_csv(url)
        df.to_excel(NETO_FILE_PATH, index=False)
        return True, NETO_FILE_PATH
    except Exception as e:
        return False, str(e)

# Função para baixar CSV do Tesouro
def baixar_csv(url, caminho_arquivo):
    try:
        resposta = requests.get(url)
        resposta.raise_for_status()
        with open(caminho_arquivo, 'wb') as arquivo:
            arquivo.write(resposta.content)
        return True, caminho_arquivo
    except Exception as e:
        return False, str(e)

# Função para enviar e-mail
def send_email(to_email, subject, body, attachment_path):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        with open(attachment_path, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename={os.path.basename(attachment_path)}',
            )
            msg.attach(part)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        
        return True, None
    except Exception as e:
        return False, str(e)

# Interface Streamlit
def main():
    st.title("📊 Extrator de Dados Financeiros")
    
    # Verifica se credenciais de e-mail estão configuradas
    if not all([EMAIL_ADDRESS, EMAIL_PASSWORD]):
        st.error("⚠️ Configuração de e-mail incompleta. Verifique o arquivo .env")

    tab1, tab2 = st.tabs(["Preço Teto", "Tesouro Direto"])

    with tab1:
        st.header("📥 Preço Teto")
        
        # Seção de Download
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬇️ Baixar Planilha"):
                success, result = download_spreadsheet()
                if success:
                    st.success(f"✅ Planilha salva em:\n{result}")
                    st.session_state.neto_downloaded = True
                else:
                    st.error(f"❌ Falha no download:\n{result}")
                    st.session_state.neto_downloaded = False

        # Seção de Envio por E-mail
        with col2:
            st.subheader("Enviar por E-mail")
            
            if not os.path.exists(NETO_FILE_PATH) and not st.session_state.get('neto_downloaded'):
                st.warning("⚠️ Faça o download da planilha primeiro!")
            else:
                to_email = st.text_input("Destinatário:", placeholder="email@exemplo.com")
                subject = st.text_input("Assunto:", value="Planilha de Investimentos")
                body = st.text_area("Mensagem:", value="Segue em anexo a planilha solicitada.")
                
                if st.button("✉️ Enviar E-mail"):
                    if not to_email or "@" not in to_email:
                        st.warning("Por favor, insira um e-mail válido")
                    else:
                        success, error_msg = send_email(to_email, subject, body, NETO_FILE_PATH)
                        if success:
                            st.success("✅ E-mail enviado com sucesso!")
                        else:
                            st.error(f"❌ Falha no envio: {error_msg}")

    with tab2:
        st.header("📥 Tesouro Direto")
        
        # Seção de Download
        if st.button("⬇️ Baixar CSV"):
            success, result = baixar_csv(TESOURO_URL, TESOURO_FILE_PATH)
            if success:
                st.success(f"✅ Arquivo salvo em:\n{result}")
                st.session_state.tesouro_downloaded = True
            else:
                st.error(f"❌ Falha no download:\n{result}")
                st.session_state.tesouro_downloaded = False

if __name__ == "__main__":
    if 'neto_downloaded' not in st.session_state:
        st.session_state.neto_downloaded = False
    if 'tesouro_downloaded' not in st.session_state:
        st.session_state.tesouro_downloaded = False
    main()