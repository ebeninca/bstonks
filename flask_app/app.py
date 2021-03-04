'''
Formula de greenblatt
Formula de Graham
Valuation DCF
Modelo de Gordon
'''
from flask import Flask, render_template
from flask_bootstrap import Bootstrap

import logging
import os

from views.greenblatt import bpGreenblatt
from views.graham import bpGraham
from views.imposto import bpImposto

app = Flask(__name__)
app.register_blueprint(bpGreenblatt)
app.register_blueprint(bpGraham)
app.register_blueprint(bpImposto)

port = int(os.environ.get("PORT", 5000))
bootstrap = Bootstrap(app)


@app.route('/')
def index():
    app.logger.info("### index ###")
    return render_template('index.jinja')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=port)
