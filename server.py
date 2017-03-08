'''flask based server'''
from flask import Flask
from flask import request
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
import entropy.utils.webio as webio
from entropy.fund.fundRoutes import fund_api
from entropy.portfolio.portfolioRoutes import portfolio_api

# init app
app = Flask(__name__)

# global app settings
app.json_encoder = webio.customJSONEncoder # centralized formatter for dates
CORS(app, origins='*') # make this restrict to same host but any port
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

@app.before_request
def log_request_info():
    if request.method != 'OPTIONS':
        print('METHOD: ', request.method)
        print('DATA: ', request.get_json())

# instead of return json( data ) everywhere, add a after_request to process in one place

@app.errorhandler(Exception)
def handle_error(e):
    code = e.code if isinstance(e, HTTPException) else 500
    return webio.err(e), code

# fund routes
app.register_blueprint(fund_api, url_prefix='/fund-data')

# portfolio routes
app.register_blueprint(portfolio_api, url_prefix='/portfolio-data')

if __name__ == '__main__':
    app.run()
