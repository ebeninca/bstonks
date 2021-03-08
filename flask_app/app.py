'''
Formula de greenblatt
Formula de Graham
Valuation DCF
Modelo de Gordon
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

# app.extensions['bootstrap']['cdns']['jquery'] = WebCDN(
#    '//cdnjs.cloudflare.com/ajax/libs/jquery/2.1.1/'
# )

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
