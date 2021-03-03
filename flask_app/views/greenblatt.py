from flask import Flask, Blueprint, render_template, current_app

import requests
import json
import logging

bpGreenblatt = Blueprint('greenblatt', __name__)


@bpGreenblatt.route('/greenblatt')
def greenblatt():
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
            
        stock['p_L'] = '%.2f' % stock['p_L']
        stock['eV_Ebit'] = 0 if "eV_Ebit" not in stock else '%.2f' % stock['eV_Ebit']
        stock['roe'] = '%.2f' % stock['roe']
        stock['roic'] = 0 if "roic" not in stock else '%.2f' % stock['roic']

    stocksJson.sort(key=lambda x: (x["final_Score"]), reverse=True)
    return json.dumps(stocksJson), 200, {'content-type': 'application/json'}
