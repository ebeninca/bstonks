from wtforms import Form, StringField, validators


class DreForm(Form):
    tickerComplete = StringField(
        'ticker', [validators.Length(min=4, max=6)], id='ticker')
    #accept_tos = BooleanField('I accept the TOS', [validators.DataRequired()])
