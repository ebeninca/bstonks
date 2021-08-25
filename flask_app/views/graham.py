'''
http://investidor-inteligente.com/benjamin-graham-margem-de-seguranca-investimento-acoes/

Margem de segurança, comparação P/L invertido com a taxa selic, P/L invertido tem que ser maior.

O objetivo é rankear as ações pelo desconto em relação ao preço. Graham, o pai
do value investing, descreveu em seu livro, O investidor inteligente, uma
formula para determinar o valor intriseco de uma ação, ou seja seu valor real
em determinado momento.

sqrt(22.5 * vpa * lpa)

Essa formula foi usada por muito tempo por Warren Buffet, pupilo de Graham,
entretanto hoje ela é questionada, pois empresas de tecnologia costumam ter
pouco patrimonio liquido, distorcendo o resultado da formula.

https://cabotwealth.com/daily/value-investing/benjamin-grahams-value-stock-criteria/
http://seuguiadeinvestimentos.com.br/a-tecnica-de-investimento-de-benjamin-graham-ii/
https://smarttinvest.com/carteiras-recomendadas-old/dh-graham/
http://www.acaoereacao.net/defens.html

CRITERIOS AVANÇADOS:
----
Investidor Sardinha:
Cagr 5% roe 5%
Abaixo valor intrínseco
Líder setor
Dividendos 10 anos
Lucros 10 anos
Perenidade 30 anos 
----
Ação e Reação:
1. Companhias proeminentes em seus setores.
2. Vendas anuais substanciais: acima de US$ 250 milhões.
3. Sólida posição financeira: Liquidez Corrente de pelo menos 1,00 e relação Dívida Líquida/Patrimônio Líquido máxima de 50%.
4. Estabilidade de lucro: lucro e dividendos contínuos durante pelo menos 12 anos.
5. Crescimento de lucro: aumento de pelo menos 4% aa em termos reais, usando as médias dos 3 anos no início e no fim de um período de 12 anos.
6. Preço/Lucro histórico moderado: o preço atual da ação, dividido pelo lucro médio dos últimos 3 anos (corrigidos pela inflação), não deve exceder 15x.
A recomendação básica de Graham é que o Lucro/Preço médio (o inverso do Preço/Lucro médio) da carteira seja pelo menos igual à taxa de juros oferecida por bônus de boa qualidade. Hoje a NTN-B de 9 anos oferece juros de 5,1% aa em termos reais que equivale a um Lucro/Preço de 19,6x.
7. Preço/Patrimônio Líquido moderado: o indicador não deve ultrapassar 150%. Mas, seguindo Graham, aceitamos um Preço/Patrimônio Líquido maior de 150% (ou 1,5) se o produto de Preço/Patrimônio Líquido x Preço/Lucro é menor que 22,50.
'''
from flask import Flask, Blueprint, render_template, current_app, request

import requests
import json
import logging
import locale
import math

bpGraham = Blueprint('graham', __name__)


@bpGraham.route('/graham', methods=['POST', 'GET'])
def index():
    current_app.logger.info("### graham ###")
    checkSelected = False
    if request.method == 'POST':
        checkSelected = True if 'advanced' in request.form else False
    respJson = json.loads(grahamApi(checkSelected)[0])
    return render_template('graham.jinja', stocks=respJson, colnames=(respJson[0]).keys(), checkSelected=checkSelected)


@bpGraham.route('/api/graham/<advanced>')
def grahamApi(advanced):
    current_app.logger.info("### graham ###")
    locale.setlocale(locale.LC_MONETARY, '')
    resp = None

    if advanced:
        resp = requests.get(
            "https://statusinvest.com.br/category/advancedsearchresult?CategoryType=1&search={'dividaliquidaPatrimonioLiquido':{'Item1':null,'Item2':0.5},'liquidezCorrente':{'Item1':1,'Item2':null}, 'lucros_Cagr5':{'Item1':5,'Item2':null},'liquidezMediaDiaria':{'Item1':200000,'Item2':null},'roe':{'Item1':5,'Item2':null}}")
    else:
        resp = requests.get(
            "https://statusinvest.com.br/category/advancedsearchresult?CategoryType=1&search={'liquidezMediaDiaria':{'Item1':200000,'Item2':null}}")

    stocksJson = json.loads(resp.text)

    for idx in range(len(stocksJson)-1, -1, -1):
        stock = stocksJson[idx]
        if "vpa" not in stock or "lpa" not in stock or "price" not in stock:
            stocksJson.pop(idx)
            continue
        if float(stock["vpa"]) <= 0 or float(stock["lpa"]) <= 0:
            stocksJson.pop(idx)
            continue

        stock['dl_Pl'] = stock['dividaliquidaPatrimonioLiquido'] if 'dividaliquidaPatrimonioLiquido' in stock else 0
        stock['liq_Corr'] = stock['liquidezCorrente'] if 'liquidezCorrente' in stock else 0

        stock['lucros_Cagr5'] = '%.2f' % round((
            0 if 'lucros_Cagr5' not in stock else stock['lucros_Cagr5']), 2)
        stock['val_Intrinseco'] = math.sqrt(
            22.5 * float(stock['vpa']) * float(stock['lpa']))
        stock['desconto'] = float(
            stock['val_Intrinseco']) - float(stock['price'])

        stock['margem'] = ((float(
            stock['val_Intrinseco']) - float(stock['price'])) / float(stock['val_Intrinseco'])) * 100

        for key in ['companyId', 'roic', 'p_VP', 'p_Ebit', 'p_Ativo', 'margemBruta', 'margemEbit',
                    'margemLiquida', 'p_SR', 'p_CapitalGiro', 'p_AtivoCirculante', 'giroAtivos', 'roa',
                    'dividaLiquidaEbit', 'pl_Ativo', 'passivo_Ativo', 'liquidezCorrente',
                    'peg_Ratio', 'receitas_Cagr5', 'liquidezMediaDiaria', 'p_L', 'eV_Ebit',
                    'valorMercado', 'dy', 'dividaliquidaPatrimonioLiquido']:
            stock.pop(key, None)

        # stock['dividaliquidaPatrimonioLiquido'] = '%.2f' % round(
        #    stock['dividaliquidaPatrimonioLiquido'], 2)
        stock['price'] = locale.currency(stock['price'])
        stock['vpa'] = '%.2f' % round(stock['vpa'], 2)
        stock['lpa'] = '%.2f' % round(stock['lpa'], 2)
        stock['val_Intrinseco'] = locale.currency(stock['val_Intrinseco'])
        stock['desconto'] = locale.currency(stock['desconto'])

        # 'lucros_Cagr5','liquidezCorrente','dividaliquidaPatrimonioLiquido',

    stocksJson.sort(key=lambda x: (x["margem"]), reverse=True)

    for stock in stocksJson:
        stock['margem'] = ('%.2f' % round(stock['margem'], 2)) + '%'

    return json.dumps(stocksJson), 200, {'content-type': 'application/json'}
