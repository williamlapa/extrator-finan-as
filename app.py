import PySimpleGUI as sg
import requests
import os

# Função para baixar o CSV
def baixar_csv(url, diretorio, nome_arquivo):
    try:
        if not os.path.isdir(diretorio):
            sg.popup_error("Erro", "Diretório inválido!")
            return

        caminho_arquivo = os.path.join(diretorio, nome_arquivo)

        resposta = requests.get(url)
        resposta.raise_for_status()

        with open(caminho_arquivo, 'wb') as f:
            f.write(resposta.content)

        sg.popup("✅ Sucesso", f"Arquivo salvo em:\n{caminho_arquivo}")

    except requests.exceptions.RequestException as e:
        sg.popup_error("Erro de download", str(e))
    except Exception as e:
        sg.popup_error("Erro ao salvar", str(e))

# Layout da janela
layout = [
    [sg.Text('Selecione o diretório para salvar o CSV:')],
    [sg.InputText(key='diretorio'), sg.FolderBrowse('Procurar')],
    [sg.Button('Baixar CSV'), sg.Button('Sair')]
]

# Criar a janela
window = sg.Window('Exportador Tesouro Direto', layout)

# URL do arquivo e nome
url = "https://www.tesourotransparente.gov.br/ckan/dataset/df56aa-484a-4a59-8184-7676580c81e3/resource/796d2059-14e9-44e3-80c9-2d9e30b405c1/download/PrecoTaxaTesouroDireto.csv"
nome_arquivo = "PrecoTaxaTesouroDireto.csv"

# Loop de eventos
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Sair':
        break
    if event == 'Baixar CSV':
        diretorio = values['diretorio']
        baixar_csv(url, diretorio, nome_arquivo)

window.close()
