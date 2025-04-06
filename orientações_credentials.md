O arquivo `credentials.json` contém as credenciais de autenticação geradas pelo Google Cloud Console para permitir o acesso programático à API do Google. Ele inclui informações sensíveis de autenticação, como o ID do cliente, secret key, e configurações específicas da conta de serviço.

Aqui está como configurar o arquivo `credentials.json`.

---

### **Gerar o `credentials.json`**

1. **Acesse o Google Cloud Console**:

   - URL: [Google Cloud Console](https://console.cloud.google.com/)
2. **Crie um projeto ou use um existente**:

   - Clique em "Selecione um projeto" e crie um novo (ou escolha um existente).
3. **Ative a API Google Drive**:

   - No painel do projeto, clique em **API e Serviços > Biblioteca**.
   - Procure por "Google Drive API" e ative a API.
4. **Configure uma conta de serviço**:

   - Vá para **API e Serviços > Credenciais**.
   - Clique em "Criar credenciais" e escolha "Conta de serviço".
   - Configure a conta de serviço com um nome que você reconheça (ex.: `my-service-account`).
   - Vincule permissões necessárias à conta (caso não tenha certeza, atribua a função "Editor").
   - Conclua e baixe o arquivo `.json`.
5. **Compartilhe a planilha com a conta de serviço**:

   - O e-mail associado à conta de serviço estará no formato:
     ```
     your-service-account-name@your-project-id.iam.gserviceaccount.com
     ```
   - Compartilhe a planilha no Google Drive com este e-mail, garantindo ao menos permissão de **Leitura** ou **Edição**.

---

### **Estrutura do `credentials.json`**

Aqui está um exemplo do conteúdo típico de `credentials.json` gerado pelo Google Cloud Console:

```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "your-private-key-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\nYOUR-PRIVATE-KEY-HERE\n-----END PRIVATE KEY-----\n",
  "client_email": "your-service-account-name@your-project-id.iam.gserviceaccount.com",
  "client_id": "your-client-id",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account-name%40your-project-id.iam.gserviceaccount.com"
}
```

---

### **Explicação dos campos**:

1. **`type`**:

   - Identifica o tipo de autenticação. Será sempre `"service_account"`.
2. **`project_id`**:

   - ID do projeto no Google Cloud. Você encontra isso no painel de projeto.
3. **`private_key_id`**:

   - Identificador da chave privada usada na autenticação.
4. **`private_key`**:

   - Chave privada que autentica o acesso à API (nunca compartilhe este valor publicamente).
5. **`client_email`**:

   - O e-mail vinculado à conta de serviço. Use-o para compartilhar a planilha no Google Drive.
6. **`auth_uri`, `token_uri`, `auth_provider_x509_cert_url`, `client_x509_cert_url`**:

   - URLs usadas pela API para autenticação e troca de tokens.

---

### **Passos após configurar o arquivo `credentials.json`**:

- Certifique-se de que o arquivo JSON está salvo em um local seguro.
- No código, ajuste o caminho para o arquivo (`credenciais_json`) ao local onde você salvou o arquivo.

---

### **Avisos importantes**:

- **Permissões**: Compartilhar a planilha apenas com o e-mail vinculado à conta de serviço garante que apenas este script tem acesso.
- **Segurança**: Nunca exponha ou distribua o arquivo `credentials.json`, especialmente a chave privada (`private_key`).
