from flask import Flask, request
from flask_cors import CORS, cross_origin
import dbio
import analytics
import constants
import dbclient
from utils import json
import utils

# init app
app = Flask(__name__);
app.json_encoder = utils.customJSONEncoder # centralized formatter for dates
CORS(app)

# init db
client = dbclient.MClient()

# fund Page
@app.route('/fund-data/nav/<schemeCode>')
def getFundNav( schemeCode ):
    return json( dbio.fundNav( client, schemeCode ) )

@app.route('/fund-data/return/<schemeCode>/<window>')
def getFundReturn( schemeCode, window ):
    return json( analytics.fundReturn( client, schemeCode, window ) )

@app.route('/fund-data/schemes')
def getFundSchemes():
    return json( dbio.fundSchemes( client ) )

@app.route('/fund-data/schemes/<navDate>')
def getFundSchemesForDate( navDate ):
    return json( dbio.fundSchemes( client, utils.dateParser( navDate ) ) )

@app.route('/fund-data/scheme/<schemeCode>')
def getFundScheme( schemeCode ):
    return json( dbio.fundScheme( client, schemeCode ) )

# portfolio Page
@app.route('/portfolio-data/client/<clientName>')
def getClientPortfolios( clientName ):
    return json( dbio.clientPortfolios( client, clientName ) )

@app.route('/portfolio-data/<portfolioId>')
def getPortfolio( portfolioId ):
    return json( dbio.portfolioData( client, portfolioId ) )

@app.route('/portfolio-data/<portfolioId>/transactions')
def getPortfolioTransactions( portfolioId ):
    return json( dbio.transactions( client, portfolioId ) )

@app.route('/portfolio-data/new',methods=['POST'])
def addPortfolio():
    ack = dbio.addPortfolio( client, request[ constants.CLIENT_NAME ], request[ constants.PORTFOLIO_NAME ] );
    return json( ack )

@app.route('/portfolio-data/<portfolioId>/transaction/new',methods=['POST'])
def addTransaction( portfolioId ):
    data = request.get_json();
    ack = dbio.addTransaction( client, portfolioId, data[ constants.ASSET_CODE ], data[ constants.ASSET_NAME ],
        data[ constants.TXN_CASHFLOW ], data[ constants.TXN_QUANTITY ], utils.dateParser( data[ constants.TXN_DATE ] ) );
    return json( ack )

@app.route('/portfolio-data/<portfolioId>/transaction/<transactionId>',methods=['DELETE'])
def removeTransaction( portfolioId, transactionId ):
    # todo: add elif for PUT (Modify)
    if request.method == 'DELETE':
        ack = dbio.removeTransaction( client, portfolioId, int(transactionId) )
        return( json( ack ) )

app.config['PROPAGATE_EXCEPTIONS'] = True
@app.before_request
def log_request_info():
    print('\nMETHOD: ', request.method);
    print('HEADERS: ', request.headers);
    print('DATA: ', request.get_json(), '\n');

# instead of return json( data ) everywhere, add a after_request to process in one place

if __name__ == '__main__':
    app.run();