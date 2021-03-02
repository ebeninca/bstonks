'''
Formula de greenblatt
Formula de Graham
Valuation DCF
Modelo de Gordon
'''
from flask import Flask
from flask import render_template
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import Navbar, View

import requests
import json
import logging
import os
# from threading import Timer
import webbrowser
# from livereload import Server

app = Flask(__name__)
port = int(os.environ.get("PORT", 5000))

bootstrap = Bootstrap(app)
nav = Nav()
nav.init_app(app)


@nav.navigation()
def mynavbar():
    app.logger.info("### mynavbar ###")
    # return Navbar(
    #     'Macas Stonks',
    #     View('Home', 'index'),
    #     View('Greenblatt', 'greenblatt'),
    # )
    menus = [('greenblatt', 'Greenblatt'),
             ('index', 'Home')]
    return menus


@app.route('/')
def index():
    app.logger.info("### index ###")
    return render_template('index.jinja')


@app.route('/greenblatt')
def greenblatt():
    app.logger.info("### greenblatt ###")
    respJson = json.loads(greenblattApi()[0])
    return render_template('greenblatt.jinja', stocks=respJson, colnames=(respJson[0]).keys())


# TODO eV_Ebit e roic
@ app.route('/api/greenblatt')
def greenblattApi():
    app.logger.info("### greenblattApi ###")
    resp = requests.get(
        "https://statusinvest.com.br/category/advancedsearchresult?CategoryType=1&search={}")
    stocksJson = json.loads(resp.text)

    for idx in range(len(stocksJson)-1, -1, -1):
        stock = stocksJson[idx]
        if "liquidezMediaDiaria" not in stock or int(stock["liquidezMediaDiaria"]) < 200000:
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
        stock['final_Score'] = int(stock['pL_Score']) + int(stock['roe_Score'])
        for key in ['companyId', 'price', 'p_VP', 'p_Ebit', 'p_Ativo', 'margemBruta', 'margemEbit', 'margemLiquida',
                    'p_SR', 'p_CapitalGiro', 'p_AtivoCirculante', 'giroAtivos', 'roa',
                    'dividaliquidaPatrimonioLiquido', 'dividaLiquidaEbit', 'pl_Ativo', 'passivo_Ativo',
                    'liquidezCorrente', 'peg_Ratio', 'receitas_Cagr5', 'liquidezMediaDiaria', 'vpa', 'lpa',
                    'valorMercado', 'lucros_Cagr5', 'dy']:
            stock.pop(key, None)

    stocksJson.sort(key=lambda x: (x["final_Score"]), reverse=True)
    return json.dumps(stocksJson), 200, {'content-type': 'application/json'}


def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')


if __name__ == '__main__':
    # app.run()
    # Timer(1, open_browser).start()
    app.run(debug=True, host='0.0.0.0', port=port)
    # server = Server(app.wsgi_app)
    # server.serve(debug=True, port=5000)
