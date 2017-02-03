from flask import Flask, request
from flask_cors import CORS
import entropy.utils.io as io
from entropy.fund.fundRoutes import fund_api
from entropy.portfolio.portfolioRoutes import portfolio_api

# init app
app = Flask(__name__)

# global app settings
app.json_encoder = io.customJSONEncoder # centralized formatter for dates
CORS(app,origins='*') # make this restrict to same host but any port
app.config['PROPAGATE_EXCEPTIONS'] = True

@app.before_request
def log_request_info():
    if request.method != 'OPTIONS':
        print('METHOD: ', request.method)
        print('DATA: ', request.get_json())

# instead of return json( data ) everywhere, add a after_request to process in one place

# fund routes
app.register_blueprint(fund_api,url_prefix='/fund-data')

# portfolio routes
app.register_blueprint(portfolio_api,url_prefix='/portfolio-data')

if __name__ == '__main__':
    app.run()