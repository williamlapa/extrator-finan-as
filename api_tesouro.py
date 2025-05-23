
import urllib3
urllib3.disable_warnings()
import json
import requests
import pandas as pd
from datetime import datetime

# Verifica se mercado está aberto ou fechado
# ...existing code...
def status_mercado_df():
    url = 'https://www.tesourodireto.com.br/json/br/com/b3/tesourodireto/service/api/treasurybondsinfo.json'
    resp_dict = requests.get(url, verify=False).json()
    mkt = resp_dict['response']['TrsrBondMkt']
    
    # Converte datas e horários para o formato desejado
    abertura_data = datetime.strptime(mkt['opngDtTm'][:10], "%Y-%m-%d").strftime("%d/%m/%Y")
    abertura_hora = mkt['opngDtTm'][11:16]
    fechamento_data = datetime.strptime(mkt['clsgDtTm'][:10], "%Y-%m-%d").strftime("%d/%m/%Y")
    fechamento_hora = mkt['clsgDtTm'][11:16]
    status = mkt['sts']
    
    df = pd.DataFrame([{
        'Status': status,
        'Data Abertura': abertura_data,
        'Horário de Abertura': abertura_hora,
        'Data Fechamento': fechamento_data,
        'Horário de Fechamento': fechamento_hora        
    }])
    return df


def consultaTD(op,tp):
    """
    op:'C','V','' para Compra, Venda ou ambos
    tp:'S','P','I', '' para Selic, Prefixado, IPCA ou todos
    """
    op = op
    tp = tp
    
    url = 'https://www.tesourodireto.com.br/json/br/com/b3/tesourodireto/service/api/treasurybondsinfo.json'
    resp_dict = requests.get(url,verify=False).json()
    
    n_titulos = len(resp_dict['response']['TrsrBdTradgList'])
    
    tipos = []
    nomes = []
    tx_compras = []
    tx_vendas = []
    p_compras = []
    p_vendas = []
    vencimentos = []
    
    
    for i in range(n_titulos):
        tipos.append(resp_dict['response']['TrsrBdTradgList'][i]['TrsrBd']['FinIndxs']['nm']) 
        nomes.append(resp_dict['response']['TrsrBdTradgList'][i]['TrsrBd']['nm'])
        vencimentos.append(resp_dict['response']['TrsrBdTradgList'][i]['TrsrBd']['mtrtyDt'])
        tx_compras.append(resp_dict['response']['TrsrBdTradgList'][i]['TrsrBd']['anulInvstmtRate'])
        p_compras.append(resp_dict['response']['TrsrBdTradgList'][i]['TrsrBd']['untrInvstmtVal'])
        tx_vendas.append(resp_dict['response']['TrsrBdTradgList'][i]['TrsrBd']['anulRedRate'])
        p_vendas.append(resp_dict['response']['TrsrBdTradgList'][i]['TrsrBd']['untrRedVal']) 
    
    
    df = pd.DataFrame()
    df['Tipo'] = tipos
    df['Título'] = nomes
    df['Vencimento'] = pd.to_datetime(vencimentos)
    df['Rentabilidade (Compra)'] = tx_compras
    df['Preço R$ (Compra)'] = p_compras    
    df['Rentabilidade (Venda)'] = tx_vendas
    df['Preço R$ (Venda)'] = p_vendas
    
    if tp == 'S':
        df = df.iloc[df[df['Tipo']=='SELIC'].index]
    elif tp == 'P':
        df = df.iloc[df[df['Tipo']=='PREFIXADO'].index]
    elif tp == 'I':
        df = df.iloc[df[df['Tipo']=='IPCA'].index]
    else:
        df = df
        
    if op == 'C':
        return df[df['Preço R$ (Compra)']!=0].drop(df.columns[[5, 6]],axis=1)
    elif op == 'V':
        return df.drop(df.columns[[3, 4]],axis=1)
    else:
        return df

