"""
https://clubedovalor.com.br/blog/melhores-fiis-s-rank/

Adaptação da formula de srank para fundos imobiliarios criado pelo Clube do Valor (Ramiro)

>
Isso porque, com base no Value Investing, buscamos os FIIs com menor Preço por Valor Patrimonial (ou seja, os mais baratos) e com maior Dividend Yield pago (ou seja, com mais valor intrínseco).

Depois desses dois ranqueamentos, as posições dos FIIs são somadas e um novo ranking é feito a partir da soma delas.

Nós compramos os 15 melhores FIIs desse ranking.

"""
from flask import Flask, Blueprint, render_template, current_app, request

import requests
import json
import logging
import locale

bpSRank = Blueprint('srank', __name__)


@bpSRank.route('/srank', methods=['POST', 'GET'])
def index():
    current_app.logger.info("### srank ###")
    selectedType = 'cat1'
    form = request.form
    if form.get('typeSelect') is not None and request.method == 'POST':
        selectedType = form.get('typeSelect')
    respJson = json.loads(srank_api(selectedType)[0])
    return render_template('srank.jinja', stocks=respJson, colnames=(respJson[0]).keys(), selectedType=selectedType)


@bpSRank.route('/api/srank/<category>')
def srank_api(category):
    current_app.logger.info("### srankApi ###")
    locale.setlocale(locale.LC_MONETARY, '')

    resp = requests.get(
        'https://statusinvest.com.br/category/advancedsearchresult?CategoryType=2&search={"liquidezMediaDiaria":{"Item1":200000,"Item2":null}}')
    stocksJson = json.loads(resp.text)

    fiisDesenv = requests.get(
        'https://statusinvest.com.br/category/advancedsearchresult?CategoryType=2&search={"Segment":"87","liquidezMediaDiaria":{"Item1":200000,"Item2":null}}')
    fiisDesenvJson = json.loads(fiisDesenv.text)

    param1 = 'dy'
    param2 = 'p_vp'

    for idx in range(len(stocksJson)-1, -1, -1):
        stock = stocksJson[idx]
        if param1 not in stock or param2 not in stock:
            stocksJson.pop(idx)
            continue
        if float(stock[param1]) <= 0.00 or float(stock[param2]) <= 0.00:
            stocksJson.pop(idx)
            continue
        for idx2 in range(len(fiisDesenvJson)-1, -1, -1):
            fiiDesenv = fiisDesenvJson[idx2]
            if stock == fiiDesenv:
                stocksJson.pop(idx)
                continue

    stocksJson.sort(key=lambda x: (x[param1]))
    for idx, stock in enumerate(stocksJson):
        stock[param1 + '_Score'] = idx

    stocksJson.sort(key=lambda x: (x[param2]), reverse=True)
    for idx, stock in enumerate(stocksJson):

        stock[param2 + '_Score'] = idx
        stock['final_Score'] = int(
        stock[param1 + '_Score']) + int(stock[param2 + '_Score'])

        for key in ['companyId', 'price', 'gestao', 'liquidezmediadiaria', 'dividend_cagr', 'cota_cagr', 'percentualcaixa', 'numerocotistas']:
            stock.pop(key, None)

        stock['p_vp'] = '%.2f' % round(stock['p_vp'], 2)
        stock['dy'] = ('%.2f' % round(stock['dy'], 2))  + '%'
        stock['patrimonio'] = locale.currency(stock['patrimonio'])

    stocksJson.sort(key=lambda x: (x["final_Score"]), reverse=True)
    return json.dumps(stocksJson), 200, {'content-type': 'application/json'}
