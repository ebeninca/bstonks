"""
O objetivo aqui é montar a DRE igual do fundamentei, sem as limitações impostas,
como a API do statusinvest é aberta, então temos os dados, a dificuldade está em
transpor as colunas de anos em linhas
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
    # form = DreForm(request.form)
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

    result = [dict({"value": stock['code'], "text": stock['nameFormated']})
              for stock in companyInfoJson if stock['type'] in (1, 12)]

    return json.dumps(result), 200, {'content-type': 'application/json'}


@bpDre.route('/dre/data', methods=['POST'])
def data():
    form = request.form
    # and form.validate():
    if form.get('tickerSelect') != "" and request.method == 'POST':
        if dreApi(form.get('tickerSelect')) is None:
            return render_template('dre.jinja', message='Dados não encontrados!')
        respJson = json.loads(dreApi(form.get('tickerSelect'))[0])
        return render_template('dre.jinja', form=form, stocks=respJson,
                               colnames=(respJson[0]).keys(), ticker=form.get('tickerSelect').upper())
        # if(respJson[1] == 400):
        #    return render_template('dre.jinja', errorMsg=respJson[0])
    return render_template('dre.jinja', form=request.form)


@bpDre.route('/api/dre/<companyId>')
def dreApi(companyId):
    current_app.logger.info("### DRE API ###")

    yearNow = datetime.datetime.now().year
    callUrl = "https://statusinvest.com.br/acao/getdre?"
    callUrl += "code=" + companyId
    callUrl += "&type=0&range.min=2000"
    #callUrl += "&range.max=" + str(yearNow)

    resp = requests.get(callUrl)
    dreDataJson = json.loads(resp.text)
    if len(dreDataJson) == 0:
        return

    grid = (dreDataJson['data'])['grid']

    locale.setlocale(locale.LC_MONETARY, '')

    ''' iniciando com a coluna dos anos, nos dados retornados pelo
        statusinvest, eles tem um lista propria, separada do resto dos dados
    '''
    (dreDataJson['data'])['years'].sort(reverse=True)
    ''' copiando os anos ordenados do maior para o menor, o formato é uma lista
        de dict, porque é de facil aceitação pela biblioteca json
    '''
    finalData = [dict({'year': [year, "#000000"]})
                 for year in (dreDataJson['data'])['years']]
    # inserindo TTM no inicio da lista
    finalData.insert(0, dict({'year': ['TTM', "#000000"]}))

    ignoreKeys = ['Custos - (R$)', 'Lucro Bruto - (R$)', 'Despesas Receitas Operacionais - (R$)',
                  'Amortização Depreciação', 'EBIT - (R$)', 'Resultado não operacional - (R$)',
                  'Impostos - (R$)', 'Lucro atribuído a Controladora', 'Lucro atribuído a Não Controladores',
                  'Dívida Bruta - (R$)', 'ROIC - (%)', 'Margem Bruta - (%)', 'Margem Ebitda - (%)']

    callUrl = "https://statusinvest.com.br/acao/getbsactivepassivechart?"
    callUrl += "companyName=" + companyId
    callUrl += "&type=2"

    respPassive = requests.get(callUrl)
    passiveDataJson = json.loads(respPassive.text)

    for idxLine, line in enumerate(passiveDataJson):
        valueTmp = (str(line['patrimonioLiquido']))[:-6]
        value = ('%.2f' % float(valueTmp[:-2] + '.' + valueTmp[2:])) + "M"
        color = "#cc0000" if value.startswith("-") else "#2b1d0e"
        if idxLine == 0:
            finalData[0].update(
                {'Patrimônio Líquido': [value, color]})
        for idx, data in enumerate(finalData):
            if (data['year'])[0] == line['year']:
                finalData[idx].update(
                    {'Patrimônio Líquido': [value, color]})

    ''' vamos para a lista contendo os dados, será necessario
        transpor os dados de colunas para linhas
    '''
    for idx, content in enumerate(grid):
        # print(idx, content['isHeader'])
        ''' a primeira entrada da grid é o header, não precisamos dela,
            pois iremos pega-lo mais a frente
        '''
        if content['isHeader']:
            continue
        columns = content['columns']
        colName = ''
        countDictItems = 0

        for idxCol in range(0, len(columns)-1, 1):
            col = columns[idxCol]
            # indice 0 é o nome da coluna
            if idxCol == 0:
                # current_app.logger.debug(f'{idxCol} - {columns[idxCol]}')
                colName = col['value'].replace("/", "\x20")
                continue
            ''' indices com nome de coluna = DATA são os valores anuais, não
                temos interesse em percentuais de crescimento ano a ano
            '''
            if 'DATA' in col['name'] and colName not in ignoreKeys:
                # current_app.logger.debug(
                #    f'{idxCol} - {countDictItems} - {finalData[countDictItems]}')
                value = (col['value']).replace("\x20", "")
                if value == "-":
                    color = "#000000"
                elif "(%)" in colName:
                    color = "#cc0000" if value.startswith("-") else "#505050"
                elif "CAPEX - (R$)" in colName:
                    color = "#000000"
                elif "Dívida Líquida - (R$)" in colName:
                    color = "#228b22" if value.startswith("-") else "#cc0000"
                elif "Dívida Líquida Ebitda" in colName:
                    valueColor = float(value.replace(
                        ".", "").replace(",", "."))
                    color = "#228b22" if valueColor < 2 else \
                        "#cc0000" if valueColor > 3 else "#d4af37"
                else:
                    color = "#cc0000" if value.startswith("-") else "#228b22"

                finalData[countDictItems].update({colName: [value, color]})
                countDictItems += 1

        # stock['price'] = locale.currency(stock['price'])
        # stock['vpa'] = '%.2f' % stock['vpa']
        # stock['lpa'] = '%.2f' % stock['lpa']
        # stock['val_Intrinseco'] = locale.currency(stock['val_Intrinseco'])

    ignoreCashKeys = ['Caixa Gerado nas Operações - (R$)', 'Saldo Inicial de Caixa e Equivalentes - (R$)',
                      'Aumento de Caixa e Equivalentes - (R$)', 'Variação Cambial de Caixa e Equivalentes - (R$)',
                      'Variações nos Ativos e Passivos - (R$)', 'Depreciação e Amortização - (R$)',
                      'Lucro Líquido - (R$)', 'Equivalência Patrimonial - (R$)',
                      'Caixa Líquido Atividades de Investimento - (R$)']

    callUrl = "https://statusinvest.com.br/acao/getfluxocaixa?"
    callUrl += "code=" + companyId
    callUrl += "&type=0"

    respCash = requests.get(callUrl)
    cashDataJson = ((json.loads(respCash.text))['data'])['grid']

    for idx, content in enumerate(cashDataJson):
        if content['isHeader']:
            continue
        columnsList = content['columns']
        colName = ''
        countDictItems = 0
        for idxCol, col in enumerate(columnsList):
            if idxCol == 0:
                colName = col['value'].replace("/", "\x20")
                continue
            if 'DATA' in col['name'] and colName not in ignoreCashKeys:
                # current_app.logger.debug(
                #    f'{idxCol} - {countDictItems} - {finalData[countDictItems]}')
                value = (col['value']).replace("\x20", "")
                color = "#000000"
                if "Caixa Líquido Atividades de Financiamento - (R$)" in colName:
                    color = "#000000" if value.startswith("-") else "#cc0000"
                elif "Caixa Líquido Atividades Operacionais - (R$)" in colName:
                    color = "#cc0000" if value.startswith("-") else "#000000"

                if countDictItems == 0:
                    finalData[0].update({colName: [value, color]})
                    #finalData[0].find('Caixa Líquido Atividades Operacionais - (R$)')
                if countDictItems+1 < len(finalData):
                    finalData[countDictItems +
                              1].update({colName: [value, color]})
                    countDictItems += 1

    for idx, line in enumerate(finalData):
        fco = line.get(
            'Caixa Líquido Atividades Operacionais - (R$)', ['0', '#000000'])
        fco = float(0 if fco[0] == '-' or fco[0] ==
                    '' else fco[0].replace(".", "").replace(",", ".").replace("M", ""))
        capex = line.get('CAPEX - (R$)', ['0', '#000000'])
        capex = float(0 if capex[0] == '-' or capex[0] ==
                      '' else capex[0].replace(".", "").replace(",", "."))
        finalData[idx].update({'FCL CAPEX': [('%.2f' % (
            fco - capex)) + "M", '#228b22' if (fco - capex) >= 0.0 else '#cc0000']})

    callUrl = "https://statusinvest.com.br/acao/payoutresult?"
    callUrl += "code=" + companyId
    callUrl += "&type=2"

    respPayout = requests.get(callUrl)
    payoutDataJson = json.loads(respPayout.text)

    # print(payoutDataJson)
    if len((payoutDataJson['chart'])['series']) == 0:
        return json.dumps(finalData), 200, {'content-type': 'application/json'}

    percentualData = ((payoutDataJson['chart'])['series'])['percentual']
    proventosData = ((payoutDataJson['chart'])['series'])['proventos']
    yearsData = (payoutDataJson['chart'])['category']

    percentualData.reverse()
    proventosData.reverse()
    yearsData.reverse()

    for idxPercent in range(len(percentualData)-1, -1, -1):
        valuePerc = (percentualData[idxPercent])["value_F"]
        valueProv = (proventosData[idxPercent])["valueSmall_F"]
        year = yearsData[idxPercent]

        if value == "-":
            color_perc = "#000000"
        else:
            valuePercColor = float(
                valuePerc.replace(".", "").replace(",", ".").replace("%", ""))
            color_perc = "#cc0000" if valuePercColor < 30 else \
                "#228b22" if valuePercColor > 70 else "#d4af37"
        if idxPercent == 0:
            finalData[0].update(
                {'Proventos': [valueProv, "#d4af37"]})
            finalData[0].update(
                {'Payout': [valuePerc, color_perc]})

        for idx, data in enumerate(finalData):
            if str((data['year'])[0]) == str(year):
                finalData[idx].update(
                    {'Proventos': [valueProv, "#d4af37"]})
                finalData[idx].update(
                    {'Payout': [valuePerc, color_perc]})

    # print(years)
    # print(finalData)

    return json.dumps(finalData), 200, {'content-type': 'application/json'}
