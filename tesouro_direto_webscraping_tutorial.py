{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Tutorial de Web Scraping: Tesouro Direto\n",
    "\n",
    "Este notebook demonstra como extrair dados de títulos do Tesouro Direto usando web scraping com Python. Vamos utilizar as bibliotecas `requests` para fazer requisições HTTP e `BeautifulSoup` para analisar o HTML."
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 1. Instalando as bibliotecas necessárias\n",
    "\n",
    "Primeiro, vamos instalar as bibliotecas que precisaremos para este tutorial:"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "source": [
    "!pip install requests beautifulsoup4 pandas matplotlib"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 2. Importando as bibliotecas"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "source": [
    "import requests\n",
    "from bs4 import BeautifulSoup\n",
    "import pandas as pd\n",
    "import matplotlib.pyplot as plt\n",
    "import re\n",
    "from datetime import datetime\n",
    "import json"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 3. Obtendo os dados do Tesouro Direto\n",
    "\n",
    "Para extrair os dados do Tesouro Direto, precisamos primeiro identificar a URL correta. O site oficial do Tesouro Direto é https://www.tesourodireto.com.br/, mas vamos precisar acessar a API que fornece os dados atualizados dos títulos."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "source": [
    "# Configurando cabeçalhos para simular um navegador\n",
    "headers = {\n",
    "    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',\n",
    "    'Accept': 'application/json, text/plain, */*',\n",
    "    'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',\n",
    "    'Referer': 'https://www.tesourodireto.com.br/'\n",
    "}"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 3.1 Abordagem via API do Tesouro Direto\n",
    "\n",
    "O Tesouro Direto disponibiliza seus dados através de uma API que retorna os dados em formato JSON. Vamos acessar essa API para obter os títulos disponíveis."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "source": [
    "# URL da API que fornece os títulos disponíveis\n",
    "url_api = \"https://www.tesourodireto.com.br/json/br/com/b3/tesourodireto/service/api/treasurybondsinfo.json\"\n",
    "\n",
    "# Fazendo a requisição\n",
    "response = requests.get(url_api, headers=headers)\n",
    "\n",
    "# Verificando se a requisição foi bem-sucedida\n",
    "if response.status_code == 200:\n",
    "    print(\"Requisição bem-sucedida!\")\n",
    "    data = response.json()\n",
    "else:\n",
    "    print(f\"Erro na requisição: {response.status_code}\")\n",
    "    print(response.text)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 3.2 Explorando os dados retornados"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "source": [
    "# Analisando a estrutura dos dados\n",
    "if 'data' in response.json():\n",
    "    # Algumas vezes os dados estão dentro de uma chave 'data'\n",
    "    print(\"Estrutura dos dados:\")\n",
    "    print(json.dumps(response.json()['data'].keys(), indent=2))\n",
    "else:\n",
    "    # Caso contrário, analisamos as chaves do JSON diretamente\n",
    "    print(\"Estrutura dos dados:\")\n",
    "    print(json.dumps(list(response.json().keys()), indent=2))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "source": [
    "# Vamos tentar acessar os títulos - adaptando conforme a estrutura real dos dados\n",
    "try:\n",
    "    if 'response' in data:\n",
    "        titulos = data['response']['TrsrBdTradgList']\n",
    "    elif 'TrsrBdTradgList' in data:\n",
    "        titulos = data['TrsrBdTradgList']\n",
    "    else:\n",
    "        # Tentando outras possíveis estruturas\n",
    "        for key in data.keys():\n",
    "            if isinstance(data[key], list) and len(data[key]) > 0:\n",
    "                titulos = data[key]\n",
    "                break\n",
    "    \n",
    "    # Exibindo o primeiro título para entendermos a estrutura\n",
    "    print(\"\\nExemplo de um título:\")\n",
    "    print(json.dumps(titulos[0], indent=2))\n",
    "    \n",
    "    # Contando quantos títulos temos\n",
    "    print(f\"\\nTotal de títulos disponíveis: {len(titulos)}\")\n",
    "    \n",
    "except Exception as e:\n",
    "    print(f\"Erro ao processar os dados: {e}\")\n",
    "    print(\"Estrutura completa dos dados:\")\n",
    "    print(json.dumps(data, indent=2)[:1000]) # Limita para não mostrar tudo"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 4. Processando os dados e criando um DataFrame\n",
    "\n",
    "Vamos criar um DataFrame com os dados relevantes de cada título."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "source": [
    "# Função para extrair informações relevantes dos títulos\n",
    "def extrair_info_titulos(titulos):\n",
    "    dados = []\n",
    "    \n",
    "    for titulo in titulos:\n",
    "        try:\n",
    "            # Adaptando conforme a estrutura real dos dados\n",
    "            info = {\n",
    "                'Nome': titulo.get('TrsrBd', {}).get('nm', ''),\n",
    "                'Vencimento': titulo.get('TrsrBd', {}).get('mtrtyDt', ''),\n",
    "                'Taxa de Rendimento': titulo.get('anulInvstmtRate', ''),\n",
    "                'Preço Unitário': titulo.get('untrInvstmtVal', ''),\n",
    "                'Investimento Mínimo': titulo.get('minInvstmtAmt', ''),\n",
    "                'Tipo': titulo.get('TrsrBd', {}).get('tp', {}).get('nm', '')\n",
    "            }\n",
    "            dados.append(info)\n",
    "        except Exception as e:\n",
    "            print(f\"Erro ao processar título: {e}\")\n",
    "    \n",
    "    return dados"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "source": [
    "# Extraindo as informações e criando o DataFrame\n",
    "try:\n",
    "    dados_titulos = extrair_info_titulos(titulos)\n",
    "    df_titulos = pd.DataFrame(dados_titulos)\n",
    "    \n",
    "    # Convertendo colunas numéricas\n",
    "    for col in ['Taxa de Rendimento', 'Preço Unitário', 'Investimento Mínimo']:\n",
    "        try:\n",
    "            df_titulos[col] = pd.to_numeric(df_titulos[col].str.replace(',', '.'), errors='coerce')\n",
    "        except:\n",
    "            pass\n",
    "    \n",
    "    # Exibindo o DataFrame\n",
    "    display(df_titulos)\n",
    "    \n",
    "except Exception as e:\n",
    "    print(f\"Erro ao criar DataFrame: {e}\")\n",
    "    \n",
    "    # Alternativa: tentar uma abordagem mais genérica\n",
    "    print(\"\\nTentando abordagem alternativa...\")\n",
    "    \n",
    "    # Criar DataFrame com todos os campos disponíveis\n",
    "    df_titulos = pd.json_normalize(titulos)\n",
    "    display(df_titulos.head())"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 5. Abordagem alternativa: Web Scraping direto do site\n",
    "\n",
    "Se a abordagem da API não funcionar corretamente, podemos tentar fazer web scraping diretamente do site do Tesouro Direto."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "source": [
    "# URL da página principal do Tesouro Direto\n",
    "url_site = \"https://www.tesourodireto.com.br/titulos/precos-e-taxas.htm\"\n",
    "\n",
    "# Fazendo a requisição\n",
    "response_site = requests.get(url_site, headers=headers)\n",
    "\n",
    "# Verificando se a requisição foi bem-sucedida\n",
    "if response_site.status_code == 200:\n",
    "    print(\"Requisição ao site bem-sucedida!\")\n",
    "    soup = BeautifulSoup(response_site.content, 'html.parser')\n",
    "else:\n",
    "    print(f\"Erro na requisição ao site: {response_site.status_code}\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "source": [
    "# Localizando a tabela de títulos\n",
    "try:\n",
    "    tabelas = soup.find_all('table')\n",
    "    print(f\"Número de tabelas encontradas: {len(tabelas)}\")\n",
    "    \n",
    "    # Se houver tabelas, vamos tentar extrair os dados da primeira\n",
    "    if tabelas:\n",
    "        # Extraindo os cabeçalhos\n",
    "        headers = []\n",
    "        header_row = tabelas[0].find('thead').find('tr')\n",
    "        if header_row:\n",
    "            headers = [th.get_text(strip=True) for th in header_row.find_all('th')]\n",
    "        \n",
    "        # Extraindo os dados das linhas\n",
    "        rows = []\n",
    "        for tr in tabelas[0].find('tbody').find_all('tr'):\n",
    "            row = [td.get_text(strip=True) for td in tr.find_all('td')]\n",
    "            rows.append(row)\n",
    "        \n",
    "        # Criando o DataFrame\n",
    "        df_site = pd.DataFrame(rows, columns=headers)\n",
    "        display(df_site)\n",
    "    else:\n",
    "        print(\"Nenhuma tabela encontrada na página.\")\n",
    "        \n",
    "        # Tentando encontrar os dados em formato estruturado no JavaScript da página\n",
    "        scripts = soup.find_all('script')\n",
    "        dados_encontrados = False\n",
    "        \n",
    "        for script in scripts:\n",
    "            if script.string and 'treasuryBondsTrades' in script.string:\n",
    "                print(\"Dados encontrados no JavaScript da página!\")\n",
    "                dados_encontrados = True\n",
    "                # Extrair dados do JavaScript usando regex\n",
    "                pattern = r'treasuryBondsTrades\\s*=\\s*(\\[.*?\\]);'\n",
    "                match = re.search(pattern, script.string, re.DOTALL)\n",
    "                if match:\n",
    "                    json_data = match.group(1)\n",
    "                    dados_js = json.loads(json_data)\n",
    "                    df_js = pd.json_normalize(dados_js)\n",
    "                    display(df_js.head())\n",
    "                break\n",
    "        \n",
    "        if not dados_encontrados:\n",
    "            print(\"Não foi possível encontrar os dados dos títulos na página.\")\n",
    "            \n",
    "except Exception as e:\n",
    "    print(f\"Erro ao extrair dados da tabela: {e}\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 6. Analisando os dados"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "source": [
    "# Função para formatar os dados de forma adequada\n",
    "def formatar_dataframe(df):\n",
    "    try:\n",
    "        # Cópia do DataFrame para não modificar o original\n",
    "        df_formatado = df.copy()\n",
    "        \n",
    "        # Convertendo valores monetários para float\n",
    "        colunas_monetarias = [col for col in df.columns if 'valor' in col.lower() or 'preço' in col.lower() or 'investimento' in col.lower()]\n",
    "        for col in colunas_monetarias:\n",
    "            if col in df.columns:\n",
    "                df_formatado[col] = df_formatado[col].astype(str).str.replace('R$', '').str.replace('.', '').str.replace(',', '.').astype(float)\n",
    "        \n",
    "        # Convertendo percentuais para float\n",
    "        colunas_percentuais = [col for col in df.columns if 'taxa' in col.lower() or 'rentabilidade' in col.lower() or '%' in col.lower()]\n",
    "        for col in colunas_percentuais:\n",
    "            if col in df.columns:\n",
    "                df_formatado[col] = df_formatado[col].astype(str).str.replace('%', '').str.replace(',', '.').astype(float)\n",
    "        \n",
    "        # Convertendo datas\n",
    "        colunas_data = [col for col in df.columns if 'data' in col.lower() or 'vencimento' in col.lower()]\n",
    "        for col in colunas_data:\n",
    "            if col in df.columns:\n",
    "                try:\n",
    "                    df_formatado[col] = pd.to_datetime(df_formatado[col], format='%d/%m/%Y', errors='coerce')\n",
    "                except:\n",
    "                    pass\n",
    "        \n",
    "        return df_formatado\n",
    "    \n",
    "    except Exception as e:\n",
    "        print(f\"Erro ao formatar DataFrame: {e}\")\n",
    "        return df"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "source": [
    "# Tentando formatar o DataFrame obtido\n",
    "try:\n",
    "    if 'df_titulos' in locals():\n",
    "        df_formatado = formatar_dataframe(df_titulos)\n",
    "        display(df_formatado)\n",
    "    elif 'df_site' in locals():\n",
    "        df_formatado = formatar_dataframe(df_site)\n",
    "        display(df_formatado)\n",
    "    elif 'df_js' in locals():\n",
    "        df_formatado = formatar_dataframe(df_js)\n",
    "        display(df_formatado)\n",
    "    else:\n",
    "        print(\"Nenhum DataFrame disponível para formatação.\")\n",
    "except Exception as e:\n",
    "    print(f\"Erro ao processar DataFrame: {e}\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 7. Visualizando os dados"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "source": [
    "# Configurando o estilo dos gráficos\n",
    "plt.style.use('ggplot')\n",
    "plt.rcParams['figure.figsize'] = (12, 6)\n",
    "plt.rcParams['font.size'] = 12"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "source": [
    "# Visualizando as taxas de rendimento por tipo de título\n",
    "try:\n",
    "    if 'df_formatado' in locals():\n",
    "        # Identificando colunas relevantes\n",
    "        col_tipo = next((col for col in df_formatado.columns if 'tipo' in col.lower()), None)\n",
    "        col_taxa = next((col for col in df_formatado.columns if 'taxa' in col.lower()), None)\n",
    "        \n",
    "        if col_tipo and col_taxa:\n",
    "            plt.figure(figsize=(12, 6))\n",
    "            df_formatado.groupby(col_tipo)[col_taxa].mean().sort_values().plot(kind='barh', color='skyblue')\n",
    "            plt.title('Taxa Média de Rendimento por Tipo de Título')\n",
    "            plt.xlabel('Taxa de Rendimento (%)')\n",
    "            plt.tight_layout()\n",
    "            plt.show()\n",
    "        else:\n",
    "            print(\"Colunas necessárias não encontradas para visualização.\")\n",
    "    else:\n",
    "        print(\"DataFrame formatado não disponível.\")\n",
    "except Exception as e:\n",
    "    print(f\"Erro ao criar visualização: {e}\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "source": [
    "# Visualizando a relação entre vencimento e taxa de rendimento\n",
    "try:\n",
    "    if 'df_formatado' in locals():\n",
    "        # Identificando colunas relevantes\n",
    "        col_vencimento = next((col for col in df_formatado.columns if 'vencimento' in col.lower()), None)\n",
    "        col_taxa = next((col for col in df_formatado.columns if 'taxa' in col.lower()), None)\n",
    "        col_tipo = next((col for col in df_formatado.columns if 'tipo' in col.lower()), None)\n",
    "        \n",
    "        if col_vencimento and col_taxa:\n",
    "            plt.figure(figsize=(12, 6))\n",
    "            if col_tipo:\n",
    "                for tipo, grupo in df_formatado.groupby(col_tipo):\n",
    "                    plt.scatter(grupo[col_vencimento], grupo[col_taxa], label=tipo, alpha=0.7)\n",
    "                plt.legend()\n",
    "            else:\n",
    "                plt.scatter(df_formatado[col_vencimento], df_formatado[col_taxa], alpha=0.7, color='blue')\n",
    "            \n",
    "            plt.title('Relação entre Data de Vencimento e Taxa de Rendimento')\n",
    "            plt.xlabel('Data de Vencimento')\n",
    "            plt.ylabel('Taxa de Rendimento (%)')\n",
    "            plt.grid(True)\n",
    "            plt.tight_layout()\n",
    "            plt.show()\n",
    "        else:\n",
    "            print(\"Colunas necessárias não encontradas para visualização.\")\n",
    "    else:\n",
    "        print(\"DataFrame formatado não disponível.\")\n",
    "except Exception as e:\n",
    "    print(f\"Erro ao criar visualização: {e}\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 8. Salvando os dados em arquivo CSV"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "source": [
    "# Salvando os dados obtidos em um arquivo CSV\n",
    "try:\n",
    "    if 'df_formatado' in locals():\n",
    "        # Obtendo a data atual para incluir no nome do arquivo\n",
    "        data_atual = datetime.now().strftime(\"%Y-%m-%d\")\n",
    "        nome_arquivo = f\"tesouro_direto_{data_atual}.csv\"\n",
    "        \n",
    "        # Salvando o DataFrame em CSV\n",
    "        df_formatado.to_csv(nome_arquivo, index=False, encoding='utf-8-sig')\n",
    "        print(f\"Dados salvos com sucesso no arquivo '{nome_arquivo}'\")\n",
    "    else:\n",
    "        print(\"Nenhum DataFrame formatado disponível para salvar.\")\n",
    "except Exception as e:\n",
    "    print(f\"Erro ao salvar arquivo CSV: {e}\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 9. Conclusão\n",
    "\n",
    "Neste tutorial, aprendemos como extrair dados do Tesouro Direto usando web scraping com Python. Utilizamos duas abordagens:\n",
    "\n",
    "1. Através da API do Tesouro Direto, que fornece os dados em formato JSON\n",
    "2. Através do web scraping direto do site, usando BeautifulSoup para analisar o HTML\n",
    "\n",
    "Processamos os dados obtidos, criamos visualizações e salvamos os resultados em um arquivo CSV.\n",
    "\n",
    "### Observações importantes:\n",
    "\n",
    "- A estrutura dos dados no site do Tesouro Direto pode mudar ao longo do tempo, o que pode exigir ajustes no código.\n",
    "- Este tutorial é apenas para fins educacionais. Sempre verifique os termos de uso do site antes de fazer web scraping.\n",
    "- Para uso em produção, considere utilizar uma API oficial, se disponível, em vez de web scraping.\n",
    "- Os dados extraídos estão sujeitos à precisão da fonte e do processo de extração."
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 10. Recursos adicionais\n",
    "\n",
    "- [Site oficial do Tesouro Direto](https://www.tesourodireto.com.br/)\n",
    "- [Documentação do BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)\n",
    "- [Documentação do Pandas](https://pandas.pydata.org/docs/)\n",
    "- [Documentação do Matplotlib](https://matplotlib.org/stable/contents.html)"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.8.10"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}