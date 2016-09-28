from flask import Flask, jsonify
import dbio
import analytics
import constants
import dbclient
from flask_cors import CORS, cross_origin
import utils

app = Flask(__name__);
app.json_encoder = utils.customJSONEncoder;
client = dbclient.MClient();
CORS(app)
origin = '*';

def json( data ):
    return( jsonify( { constants.JSON_KEY : data } ) );

# fund Page
@app.route('/fund-data/nav/<schemeCode>')
def getFundNav( schemeCode ):
    return json( dbio.fundNav( client, schemeCode ) );

@app.route('/fund-data/return/<schemeCode>/<window>')
def getFundReturn( schemeCode, window ):
    return json( analytics.fundReturn( client, schemeCode, window ) );

@app.route('/fund-data/schemes')
def getFundSchemes():
    return json( dbio.fundSchemes( client ) );

@app.route('/fund-data/scheme/<schemeCode>')
def getFundScheme( schemeCode ):
    return json( dbio.fundScheme( client, schemeCode ) );

# portfolio Page
@app.route('/portfolio-data/client/<clientName>')
def getClientPortfolios( clientName ):
    return json( dbio.clientPortfolios( client, clientName ) );

@app.route('/portfolio-data/<portfolioId>')
def getPortfolio( portfolioId ):
    return json( dbio.portfolioData( client, portfolioId ) );

@app.route('/portfolio-data/<portfolioId>/transactions')
def getPortfolioTransactions( portfolioId ):
    return json( dbio.transactions( client, portfolioId ) );

@app.route('/portfolio-data/new',methods=['POST'])
def addPortfolio():
    ack = dbio.addPortfolio( client, request[ constants.CLIENT_NAME ], request[ constants.PORTFOLIO_NAME ] );
    return ack;

@app.route('/portfolio-data/<portfolioId>/transaction/new',methods=['POST'])
def addTransaction():
    ack = dbio.addTransaction( client, portfolioId, request[ ASSET_CODE ], request[ TXN_QUANTITY ], request[ TXN_DATE ] );
    return ack;

app.config['PROPAGATE_EXCEPTIONS'] = True

if __name__ == '__main__':
    app.run();