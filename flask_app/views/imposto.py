from flask import Flask, Blueprint, render_template, current_app

import requests
import json
import logging
import locale
import math

bpImposto = Blueprint('imposto', __name__)


@bpImposto.route('/imposto')
def imposto():
    current_app.logger.info("### graham ###")
    respJson = json.loads(impostoApi()[0])
    return render_template('imposto.jinja', stocks=respJson, colnames=(respJson[0]).keys())


@bpImposto.route('/api/imposto')
def impostoApi():
    current_app.logger.info("### graham ###")
    locale.setlocale(locale.LC_MONETARY, '')
    
    resp = requests.get(
        "https://statusinvest.com.br/category/advancedsearchresult?CategoryType=1&search={}")
    stocksJson = json.loads(resp.text)

    for idx in range(len(stocksJson)-1, -1, -1):
        stock = stocksJson[idx]
        if "liquidezMediaDiaria" not in stock or int(stock["liquidezMediaDiaria"]) < 200000:
            stocksJson.pop(idx)
            continue
        if "vpa" not in stock or "lpa" not in stock or "price" not in stock:
            stocksJson.pop(idx)
            continue
        if float(stock["vpa"]) <= 0 or float(stock["lpa"]) <= 0:
            stocksJson.pop(idx)
            continue
        stock['val_Intrinseco'] = math.sqrt(22.5 * \
            float(stock['vpa']) * float(stock['lpa'])) 
        stock['desconto'] = float(
            stock['val_Intrinseco']) - float(stock['price'])

        for key in ['companyId', 'roic', 'roe', 'p_VP', 'p_Ebit', 'p_Ativo', 'margemBruta', 'margemEbit',
                    'margemLiquida', 'p_SR', 'p_CapitalGiro', 'p_AtivoCirculante', 'giroAtivos', 'roa',
                    'dividaliquidaPatrimonioLiquido', 'dividaLiquidaEbit', 'pl_Ativo', 'passivo_Ativo',
                    'liquidezCorrente', 'peg_Ratio', 'receitas_Cagr5', 'liquidezMediaDiaria', 'p_L', 'eV_Ebit',
                    'valorMercado', 'lucros_Cagr5', 'dy']:
            stock.pop(key, None)

        stock['price'] = locale.currency(stock['price'])
        stock['vpa'] = '%.2f' % stock['vpa']
        stock['lpa'] = '%.2f' % stock['lpa']
        stock['val_Intrinseco'] = locale.currency(stock['val_Intrinseco'])


    stocksJson.sort(key=lambda x: (x["desconto"]), reverse=True)

    for stock in stocksJson:
        stock['desconto'] = locale.currency(stock['desconto'])

    return json.dumps(stocksJson), 200, {'content-type': 'application/json'}
