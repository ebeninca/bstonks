from flask import Flask, Blueprint, render_template, current_app

import requests
import json
import logging
import locale
import math

bpGraham = Blueprint('graham', __name__)


@bpGraham.route('/graham')
def graham():
    current_app.logger.info("### graham ###")
    respJson = json.loads(grahamApi()[0])
    return render_template('graham.jinja', stocks=respJson, colnames=(respJson[0]).keys())


@bpGraham.route('/api/graham')
def grahamApi():
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

        stock['val_Intrinseco'] = math.sqrt(22.5 *
                                            float(stock['vpa']) * float(stock['lpa']))
        stock['desconto'] = float(
            stock['val_Intrinseco']) - float(stock['price'])

        stock['margem'] = ((float(
            stock['val_Intrinseco']) - float(stock['price'])) / float(stock['val_Intrinseco'])) * 100

        for key in ['companyId', 'roic', 'roe', 'p_VP', 'p_Ebit', 'p_Ativo', 'margemBruta', 'margemEbit',
                    'margemLiquida', 'p_SR', 'p_CapitalGiro', 'p_AtivoCirculante', 'giroAtivos', 'roa',
                    'dividaliquidaPatrimonioLiquido', 'dividaLiquidaEbit', 'pl_Ativo', 'passivo_Ativo',
                    'liquidezCorrente', 'peg_Ratio', 'receitas_Cagr5', 'liquidezMediaDiaria', 'p_L', 'eV_Ebit',
                    'valorMercado', 'lucros_Cagr5', 'dy']:
            stock.pop(key, None)

        stock['price'] = locale.currency(stock['price'])
        stock['vpa'] = '%.2f' % round(stock['vpa'], 2)
        stock['lpa'] = '%.2f' % round(stock['lpa'], 2)
        stock['val_Intrinseco'] = locale.currency(stock['val_Intrinseco'])
        stock['desconto'] = locale.currency(stock['desconto'])

    stocksJson.sort(key=lambda x: (x["margem"]), reverse=True)

    for stock in stocksJson:
        stock['margem'] = ('%.2f' % round(stock['margem'], 2)) + '%'

    return json.dumps(stocksJson), 200, {'content-type': 'application/json'}
