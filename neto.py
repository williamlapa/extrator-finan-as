import streamlit as st
import pandas as pd
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

# Configurações (agora lê do .env)
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")  # Valor padrão para Gmail
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))  # Valor padrão para Gmail

# Outras configurações
SHEET_ID = os.getenv("sheet_id")
SHEET_NAME = os.getenv("sheet_name")
DOWNLOAD_FOLDER = os.getenv("download_folder")
FILE_NAME = os.getenv("file_name")
FILE_PATH = os.path.join(DOWNLOAD_FOLDER, FILE_NAME)  # Definindo FILE_PATH globalmente

# Função para download da planilha
def download_spreadsheet():
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"
        df = pd.read_csv(url)
        os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
        df.to_excel(FILE_PATH, index=False)
        return True, FILE_PATH
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
    st.title("📊 Gerenciador de Planilha")
    
    # Verifica se credenciais de e-mail estão configuradas
    if not all([EMAIL_ADDRESS, EMAIL_PASSWORD]):
        st.error("⚠️ Configuração de e-mail incompleta. Verifique o arquivo .env")

    tab1, tab2 = st.tabs(["Download Local", "Enviar por E-mail"])

    with tab1:
        if st.button("⬇️ Baixar Planilha"):
            success, result = download_spreadsheet()
            if success:
                st.success(f"✅ Planilha salva em:\n{result}")
                st.session_state.file_downloaded = True  # Marca que o download foi feito
            else:
                st.error(f"❌ Falha no download:\n{result}")
                st.session_state.file_downloaded = False

    with tab2:
        st.subheader("Enviar Planilha por E-mail")
        
        # Verifica se o download foi feito
        if not os.path.exists(FILE_PATH) and not st.session_state.get('file_downloaded'):
            st.warning("⚠️ Faça o download da planilha primeiro!")
        else:
            to_email = st.text_input("Destinatário:", placeholder="email@exemplo.com")
            subject = st.text_input("Assunto:", value="Planilha de Investimentos")
            body = st.text_area("Mensagem:", value="Segue em anexo a planilha solicitada.")
            
            if st.button("✉️ Enviar E-mail"):
                if not to_email or "@" not in to_email:
                    st.warning("Por favor, insira um e-mail válido")
                else:
                    success, error_msg = send_email(to_email, subject, body, FILE_PATH)
                    if success:
                        st.success("✅ E-mail enviado com sucesso!")
                    else:
                        st.error(f"❌ Falha no envio: {error_msg}")

if __name__ == "__main__":
    if 'file_downloaded' not in st.session_state:
        st.session_state.file_downloaded = False
    main()