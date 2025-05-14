import streamlit as st
import pandas as pd
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import requests
import platform  # ➕ Para identificar ambiente operacional
import json
import hashlib

# --- GERENCIAMENTO DE USUÁRIOS ---

USERS_FILE = "usuarios.json"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    users = []
    for key, user in st.secrets["users"].items():
        users.append({
            "email": user["email"],
            "password": hash_password(user["password"]),
            "admin": user.get("admin", False)
        })
    return users

def save_users(users):
    st.warning("Salvar usuários no TOML não é suportado em tempo de execução. Edite o arquivo secrets.toml manualmente.")

def authenticate(email, password):
    users = load_users()
    for user in users:
        if user["email"] == email and user["password"] == hash_password(password):
            return user
    return None

def user_exists(email):
    users = load_users()
    return any(u["email"] == email for u in users)

def add_user(email, password, admin=False):
    st.warning("Adicionar usuários só é possível editando o arquivo secrets.toml.")

def update_user(email, password=None, admin=None):
    st.warning("Editar usuários só é possível editando o arquivo secrets.toml.")

def remove_user(email):
    st.warning("Remover usuários só é possível editando o arquivo secrets.toml.")

# --- FIM GERENCIAMENTO DE USUÁRIOS ---

# Carrega variáveis dos secrets
EMAIL_ADDRESS = st.secrets["email"]["EMAIL_ADDRESS"]
EMAIL_PASSWORD = st.secrets["email"]["EMAIL_PASSWORD"]
SMTP_SERVER = st.secrets["email"]["SMTP_SERVER"]
SMTP_PORT = int(st.secrets["email"]["SMTP_PORT"])

# 🔄 Ajuste automático do diretório de download conforme o ambiente
if platform.system() == "Windows":
    DOWNLOAD_FOLDER = os.path.normpath(st.secrets["sheet_config"]["download_folder"])
else:
    DOWNLOAD_FOLDER = os.path.normpath("downloads")  # Pasta local padrão no Streamlit Cloud

# Garante que a pasta de download exista
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Configurações do Neto
NETO_SHEET_ID = st.secrets["sheet_config"]["sheet_id"]
NETO_SHEET_NAME = st.secrets["sheet_config"]["sheet_name"]
NETO_FILE_NAME = st.secrets["sheet_config"]["file_name"]
NETO_FILE_PATH = os.path.normpath(os.path.join(DOWNLOAD_FOLDER, NETO_FILE_NAME))

# Configurações do Tesouro
TESOURO_URL = "https://www.tesourotransparente.gov.br/ckan/dataset/df56aa42-484a-4a59-8184-7676580c81e3/resource/796d2059-14e9-44e3-80c9-2d9e30b405c1/download/PrecoTaxaTesouroDireto.csv"
TESOURO_FILE_NAME = "PrecoTaxaTesouroDireto.csv"
TESOURO_FILE_PATH = os.path.normpath(os.path.join(DOWNLOAD_FOLDER, TESOURO_FILE_NAME))

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
            part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(attachment_path)}')
            msg.attach(part)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)

        return True, None
    except Exception as e:
        return False, str(e)

# --- TELA DE LOGIN E GERENCIAMENTO DE USUÁRIOS ---
def login_screen():
    st.title("🔒 Login")
    email = st.text_input("E-mail")
    password = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        user = authenticate(email, password)
        if user:
            st.session_state.user = user
            st.success("Login realizado com sucesso!")
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos.")

def register_screen():
    st.title("Registrar novo usuário")
    email = st.text_input("Novo e-mail")
    password = st.text_input("Nova senha", type="password")
    password2 = st.text_input("Confirme a senha", type="password")
    admin = st.checkbox("Administrador")
    if st.button("Registrar"):
        if not email or not password:
            st.warning("Preencha todos os campos.")
        elif password != password2:
            st.warning("As senhas não coincidem.")
        elif user_exists(email):
            st.warning("Usuário já existe.")
        else:
            add_user(email, password, admin)
            st.success("Usuário registrado com sucesso!")
            st.session_state.show_register = False

    if st.button("Voltar para login"):
        st.session_state.show_register = False

def user_admin_screen():
    st.title("Gerenciar Usuários")
    users = load_users()
    df_users = pd.DataFrame([{"E-mail": u["email"], "Admin": u["admin"]} for u in users])
    st.dataframe(df_users, use_container_width=True)

    st.subheader("Adicionar/Editar Usuário")
    email = st.text_input("E-mail do usuário para adicionar/editar")
    new_password = st.text_input("Nova senha (deixe em branco para não alterar)", type="password")
    admin = st.checkbox("Administrador", key="admin_edit")
    if st.button("Salvar usuário"):
        if not email:
            st.warning("Informe o e-mail.")
        elif user_exists(email):
            update_user(email, password=new_password if new_password else None, admin=admin)
            st.success("Usuário atualizado.")
        else:
            if not new_password:
                st.warning("Informe a senha para novo usuário.")
            else:
                add_user(email, new_password, admin)
                st.success("Usuário adicionado.")

    st.subheader("Remover Usuário")
    email_remove = st.text_input("E-mail do usuário para remover")
    if st.button("Remover usuário"):
        if not email_remove:
            st.warning("Informe o e-mail.")
        elif email_remove == st.session_state.user["email"]:
            st.warning("Você não pode remover o próprio usuário logado.")
        elif not user_exists(email_remove):
            st.warning("Usuário não encontrado.")
        else:
            remove_user(email_remove)
            st.success("Usuário removido.")

    if st.button("Voltar"):
        st.session_state.show_user_admin = False

def change_password_screen():
    st.title("Alterar Senha")
    old_password = st.text_input("Senha atual", type="password")
    new_password = st.text_input("Nova senha", type="password")
    new_password2 = st.text_input("Confirme a nova senha", type="password")
    if st.button("Alterar senha", key="btn_alterar_senha"):
        user = st.session_state.user
        if hash_password(old_password) != user["password"]:
            st.warning("Senha atual incorreta.")
        elif new_password != new_password2:
            st.warning("As novas senhas não coincidem.")
        elif not new_password:
            st.warning("Nova senha não pode ser vazia.")
        else:
            update_user(user["email"], password=new_password)
            st.success("Senha alterada com sucesso!")
            # Atualiza a senha na sessão
            st.session_state.user["password"] = hash_password(new_password)

    if st.button("Voltar", key="btn_voltar_senha"):
        st.session_state.show_change_password = False

# --- INTERFACE PRINCIPAL ---
def main():
    if "user" not in st.session_state:
        st.session_state.user = None
    if "show_register" not in st.session_state:
        st.session_state.show_register = False
    if "show_user_admin" not in st.session_state:
        st.session_state.show_user_admin = False
    if "show_change_password" not in st.session_state:
        st.session_state.show_change_password = False

    if not st.session_state.user:
        if st.session_state.show_register:
            register_screen()
        else:
            login_screen()
        return

    # Menu superior
    st.sidebar.write(f"Usuário: {st.session_state.user['email']}")
    if st.session_state.user.get("admin"):
        if st.sidebar.button("Ir para a tela principal", key="btn_tela_principal"):
            st.session_state.show_change_password = False
            st.session_state.show_user_admin = False
            st.rerun()
        if st.sidebar.button("Alterar senha"):
            st.session_state.show_change_password = True
        if st.sidebar.button("Gerenciar usuários"):
            st.session_state.show_user_admin = True
    if st.sidebar.button("Sair"):
        st.session_state.user = None
        st.rerun()

    # Apenas admin pode acessar as telas de gerenciamento e alteração de senha
    if not st.session_state.user.get("admin"):
        st.session_state.show_change_password = False
        st.session_state.show_user_admin = False

    if st.session_state.show_change_password and st.session_state.user.get("admin"):
        change_password_screen()
        return
    if st.session_state.show_user_admin and st.session_state.user.get("admin"):
        user_admin_screen()
        return

    # --- AQUI SEGUE O RESTANTE DA SUA INTERFACE ---
    st.title("📊 Extrator de Dados Financeiros")

    if not all([EMAIL_ADDRESS, EMAIL_PASSWORD]):
        st.error("⚠️ Configuração de e-mail incompleta. Verifique o secrets.toml")

    tab1, tab2 = st.tabs(["Preço Teto", "Tesouro Direto"])

    with tab1:
        st.header("📥 Preço Teto")

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

        if st.button("⬇️ Baixar CSV"):
            success, result = baixar_csv(TESOURO_URL, TESOURO_FILE_PATH)
            if success:
                st.success(f"✅ Arquivo salvo em:\n{result}")
                st.session_state.tesouro_downloaded = True
                
                # Display latest Data Base after successful download
                try:
                    df = pd.read_csv(TESOURO_FILE_PATH, sep=';', encoding='latin1')
                    
                    if "Data Base" in df.columns:
                        df["Data Base"] = pd.to_datetime(df["Data Base"], dayfirst=True, errors='coerce')
                        latest_date = df["Data Base"].max()
                        formatted_date = latest_date.strftime('%d/%m/%Y')
                        st.info(f"📅 Data de atualização dos dados: {formatted_date}")
                    else:
                        st.warning("⚠️ A coluna 'Data Base' não foi encontrada no arquivo.")

                    # Adicionar botão de download
                    with open(TESOURO_FILE_PATH, "rb") as file:
                        st.download_button(
                            label="⬇️ Fazer Download do CSV",
                            data=file,
                            file_name=TESOURO_FILE_NAME,
                            mime="text/csv"
                        )

                except Exception as e:
                    st.error(f"❌ Falha ao ler o arquivo CSV: {str(e)}")
            else:
                st.error(f"❌ Falha no download:\n{result}")
                st.session_state.tesouro_downloaded = False

if __name__ == "__main__":
    if 'neto_downloaded' not in st.session_state:
        st.session_state.neto_downloaded = False
    if 'tesouro_downloaded' not in st.session_state:
        st.session_state.tesouro_downloaded = False
    main()
