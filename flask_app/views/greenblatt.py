"""
O objetivo aqui é rankear as ações pela formula de greenblat, temos a API do statusinvest
aberta que nos fornece os indicadores necessarios.

Existem duas versões da formula, a mais conhecida usa P/L e ROE, que atende a todo tipo
de ação, a outra usa EV/EBIT e ROIC, que não serve para bancos, pois os mesmos nao possuem
ROIC, sendo excluidos automaticamente.

As ações são ordenadas primeiro por P/L, recebendo nota, o menor P/L recebe a 
maior nota(numero total de ações que participam do ranking) e o maior P/L 
recebe 1. O mesmo processo é feito para o ROE, sendo que o maior ROE recebe a
maior nota. A soma das duas notas determina a classificação do ranking.

TODO colocar opção para calculo com EV/EVIT e ROIC
"""
from flask import Flask, Blueprint, render_template, current_app

import requests
import json
import logging

bpGreenblatt = Blueprint('greenblatt', __name__)


@bpGreenblatt.route('/greenblatt')
def index():
    current_app.logger.info("### greenblatt ###")
    respJson = json.loads(greenblattApi()[0])
    return render_template('greenblatt.jinja', stocks=respJson, colnames=(respJson[0]).keys())


@bpGreenblatt.route('/api/greenblatt')
def greenblattApi():
    current_app.logger.info("### greenblattApi ###")
    resp = requests.get(
        "https://statusinvest.com.br/category/advancedsearchresult?CategoryType=1&search={}")
    stocksJson = json.loads(resp.text)

    for idx in range(len(stocksJson)-1, -1, -1):
        stock = stocksJson[idx]
        if "liquidezMediaDiaria" not in stock or int(stock["liquidezMediaDiaria"]) < 200000:
            stocksJson.pop(idx)
            continue
        if "p_L" not in stock or "roe" not in stock:
            stocksJson.pop(idx)
            continue
        if int(stock["p_L"]) <= 0 or int(stock["roe"]) <= 0:
            stocksJson.pop(idx)
            continue

    stocksJson.sort(key=lambda x: (x["p_L"]), reverse=True)
    # stocksJson = list(map(lambda stock: exec("stock[pL_Nota]=0"), stocksJson))
    for idx, stock in enumerate(stocksJson):
        stock['pL_Score'] = idx

    stocksJson.sort(key=lambda x: (x["roe"]))
    for idx, stock in enumerate(stocksJson):
        stock['roe_Score'] = idx
        stock['final_Score'] = int(
            stock['pL_Score']) + int(stock['roe_Score'])
        for key in ['companyId', 'price', 'p_VP', 'p_Ebit', 'p_Ativo', 'margemBruta', 'margemEbit', 'margemLiquida',
                    'p_SR', 'p_CapitalGiro', 'p_AtivoCirculante', 'giroAtivos', 'roa',
                    'dividaliquidaPatrimonioLiquido', 'dividaLiquidaEbit', 'pl_Ativo', 'passivo_Ativo',
                    'liquidezCorrente', 'peg_Ratio', 'receitas_Cagr5', 'liquidezMediaDiaria', 'vpa', 'lpa',
                    'valorMercado', 'lucros_Cagr5', 'dy']:
            stock.pop(key, None)

        stock['p_L'] = '%.2f' % round(stock['p_L'], 2)
        stock['eV_Ebit'] = '%.2f' % (
            int(0) if "eV_Ebit" not in stock else round(stock['eV_Ebit'], 2))
        stock['roe'] = '%.2f' % round(stock['roe'], 2)
        stock['roic'] = '%.2f' % (
            int(0) if "roic" not in stock else round(stock['roic'], 2))

    stocksJson.sort(key=lambda x: (x["final_Score"]), reverse=True)
    return json.dumps(stocksJson), 200, {'content-type': 'application/json'}
