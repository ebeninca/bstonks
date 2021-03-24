'''
Formula de Greenblatt
Formula de Graham
Valuation DCF
Modelo de Gordon
Criterios Bazin = http://www.dinheiroinvestimentoelazer.com/2018/07/acoes-carteira-dividendos.html
Buffet indicator?

https://www.theglobaleconomy.com/Brazil/Stock_market_capitalization/
https://www.capitalinvest-group.com/pt/calcular-valor-empresa-venda-multiplos/
https://www.fool.com/investing/general/2015/02/07/why-this-67-billion-hedge-fund-strategy-doesnt-wor.aspx

'''
from flask import Flask, render_template, url_for, redirect
from flask_bootstrap import Bootstrap

import logging
import os

from views.greenblatt import bpGreenblatt
from views.graham import bpGraham
from views.dre import bpDre
from views.imposto import bpImposto

app = Flask(__name__)
app.register_blueprint(bpGreenblatt)
app.register_blueprint(bpGraham)
app.register_blueprint(bpDre)
app.register_blueprint(bpImposto)

port = int(os.environ.get("PORT", 5000))
bootstrap = Bootstrap(app)


@app.route('/')
def index():
    app.logger.info("### index ###")
    app.logger.debug(app.url_map)
    return render_template('index.jinja')


@app.route('/favicon.ico')
def favicon():
    return redirect(url_for('static', filename='dollar_sign.ico'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=port)
