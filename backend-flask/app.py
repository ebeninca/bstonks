from flask import Flask
import requests
import json
import logging
from operator import itemgetter

app = Flask(__name__)


# TODO eV_Ebit e roic
@app.route('/api/greenblatt')
def greenblatt():
    app.logger.debug("###############")
    resp = requests.get(
        "https://statusinvest.com.br/category/advancedsearchresult?CategoryType=1&search={}")

    app.logger.info("###############")
    stocksJson = json.loads(resp.text)

    for idx in range(len(stocksJson)-1, -1, -1):
        stock = stocksJson[idx]
        if "liquidezMediaDiaria" not in stock or int(stock["liquidezMediaDiaria"]) < 1000000:
            stocksJson.pop(idx)
            continue
        if int(stock["p_L"]) <= 0 or int(stock["roe"]) <= 0:
            stocksJson.pop(idx)
            continue

    stocksJson.sort(key=lambda x: (x["p_L"]), reverse=True)
    #stocksJson = list(map(lambda stock: exec("stock[pL_Nota]=0"), stocksJson))
    for idx, stock in enumerate(stocksJson):
        stock['pL_Rank'] = idx

    stocksJson.sort(key=lambda x: (x["roe"]))
    for idx, stock in enumerate(stocksJson):
        stock['roe_Rank'] = idx
        stock['final_Rank'] = int(stock['pL_Rank']) + int(stock['roe_Rank'])
        for key in ['companyId', 'price', 'p_VP', 'p_Ebit', 'p_Ativo', 'margemBruta', 'margemEbit', 'margemLiquida',
                    'p_SR', 'p_CapitalGiro', 'p_AtivoCirculante', 'giroAtivos', 'roa',
                    'dividaliquidaPatrimonioLiquido', 'dividaLiquidaEbit', 'pl_Ativo', 'passivo_Ativo',
                    'liquidezCorrente', 'peg_Ratio', 'receitas_Cagr5', 'liquidezMediaDiaria', 'vpa', 'lpa',
                    'valorMercado', 'lucros_Cagr5', 'dy']:
            stock.pop(key, None)

    stocksJson.sort(key=lambda x: (x["final_Rank"]), reverse=True)
    return json.dumps(stocksJson)


if __name__ == '__main__':
    # app.run()
    app.run(debug=True)
