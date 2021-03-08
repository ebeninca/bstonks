"""
O objetivo aqui é montar a DRE igual do fundamentei, sem as limitações impostas,
como a API do statusinvest é aberta, então temos os dados, a dificuldade está em
transpor as colunas de anos em linhas

# TODO considerar Earnings Yield (EBIT/EV e L/P)
"""
from flask import Flask, Blueprint, render_template, current_app, request

import requests
import json
import logging
import locale
import math
import datetime

from forms.dreForm import DreForm

bpDre = Blueprint('dre', __name__)


@bpDre.route('/dre')
def index():
    #form = DreForm(request.form)
    return render_template('dre.jinja')


@bpDre.route('/dre/search', methods=['GET'])
def search():
    current_app.logger.info("### DRE ###")
    if request.args.get('q') is None:
        return json.dumps([]), 200, {'content-type': 'application/json'}

    resp = requests.get(
        "https://statusinvest.com.br/home/mainsearchquery?q=" + request.args.get('q'))

    companyInfoJson = json.loads(resp.text)
    if companyInfoJson is None or len(companyInfoJson) == 0:
        return json.dumps({'Message': 'Nada foi encontrado aqui!'}), 400, {'content-type': 'application/json'}

    result = [dict({"value": stock['normalizedName'], "text": stock['name']})
              for stock in companyInfoJson]

    return json.dumps(result), 200, {'content-type': 'application/json'}


@bpDre.route('/dre/data', methods=['POST'])
def data():
    form = request.form
    print("TICKER: " + form.get('tickerSelect'))
    # and form.validate():
    if form.get('tickerSelect') is not "" and request.method == 'POST':
        respJson = json.loads(dreApi(form.get('tickerSelect'))[0])
        return render_template('dre.jinja', form=form, stocks=respJson,
                               colnames=(respJson[0]).keys())
        # if(respJson[1] == 400):
        #    return render_template('dre.jinja', errorMsg=respJson[0])
    return render_template('dre.jinja', form=request.form)


@bpDre.route('/api/dre/<companyId>')
def dreApi(companyId):
    current_app.logger.info("### DRE API ###")

    yearNow = datetime.datetime.now().year
    callUrl = "https://statusinvest.com.br/acao/getdre?"
    callUrl += "companyName=" + companyId
    callUrl += "&type=0&range.min=2000"
    callUrl += "&range.max=" + str(yearNow)

    resp = requests.get(callUrl)
    dreDataJson = json.loads(resp.text)
    grid = dreDataJson['grid']

    locale.setlocale(locale.LC_MONETARY, '')

    ''' iniciando com a coluna dos anos, nos dados retornados pelo 
        statusinvest, eles tem um lista propria, separada do resto dos dados
    '''
    dreDataJson['years'].sort(reverse=True)
    ''' copiando os anos ordenados do maior para o menor, o formato é uma lista 
        de dict, porque é de facil aceitação pela biblioteca json
    '''
    finalData = [dict({'year': year}) for year in dreDataJson['years']]
    # inserindo TTM no inicio da lista
    finalData.insert(0, dict({'year': 'TTM'}))

    ''' vamos para a lista contendo os dados, será necessario 
        transpor os dados de colunas para linhas
    '''
    for idx, content in enumerate(grid):
        # print(idx, content['isHeader'])
        ''' a primeira entrada da grid é o header, não precisamos dela, 
            pois iremos pega-lo mais a frente
        '''
        if not content['isHeader']:
            columns = content['columns']
            colName = ''
            countDictItems = 0

            for idxCol in range(0, len(columns)-1, 1):
                col = columns[idxCol]
                # indice 0 é o nome da coluna
                if idxCol == 0:
                    # current_app.logger.debug(f'{idxCol} - {columns[idxCol]}')
                    colName = col['value']
                    continue
                ''' indices com nome de coluna = DATA são os valores anuais, não
                    temos interesse em percentuais de crescimento ano a ano
                '''
                if 'DATA' in col['name']:
                    # current_app.logger.debug(
                    #    f'{idxCol} - {countDictItems} - {finalData[countDictItems]}')
                    finalData[countDictItems].update({colName: col['value']})
                    countDictItems += 1

        # stock['price'] = locale.currency(stock['price'])
        # stock['vpa'] = '%.2f' % stock['vpa']
        # stock['lpa'] = '%.2f' % stock['lpa']
        # stock['val_Intrinseco'] = locale.currency(stock['val_Intrinseco'])
    # print(years)
    # print(finalData)

    return json.dumps(finalData), 200, {'content-type': 'application/json'}
