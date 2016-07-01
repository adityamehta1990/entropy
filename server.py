from flask import Flask, jsonify
import dbio
import analytics
import constants
import dbclient
from crossdomain import *
import utils

app = Flask(__name__);
app.json_encoder = utils.customJSONEncoder;
client = dbclient.MClient();
origin = '*';

def json( data ):
    return( jsonify( { constants.JSON_KEY : data } ) );

# fund Page
@app.route('/fund-data/nav/<schemeCode>')
@crossdomain(origin=origin)
def getFundNav( schemeCode ):
    return json( dbio.fundNav( client, schemeCode ) );

@app.route('/fund-data/return/<schemeCode>/<window>')
@crossdomain(origin=origin)
def getFundReturn( schemeCode, window ):
    return json( analytics.fundReturn( client, schemeCode, window ) );

@app.route('/fund-data/schemes')
@crossdomain(origin=origin)
def getFundSchemes():
    return json( dbio.fundSchemes( client ) );

@app.route('/fund-data/scheme/<schemeCode>')
@crossdomain(origin=origin)
def getFundScheme( schemeCode ):
    return json( dbio.fundScheme( client, schemeCode ) );

# portfolio Page
@app.route('/portfolio-data/client/<clientName>')
@crossdomain(origin=origin)
def getClientPortfolios( clientName ):
    return json( dbio.clientPortfolios( client, clientName ) );

@app.route('/portfolio-data/<portfolioId>')
@crossdomain(origin=origin)
def getPortfolio( portfolioId ):
    return json( dbio.portfolioData( client, portfolioId ) );

@app.route('/portfolio-data/<portfolioId>/transactions')
@crossdomain(origin=origin)
def getPortfolioTransactions( portfolioId ):
    return json( dbio.transactions( client, portfolioId ) );

@app.route('/portfolio-data/new',methods=['POST'])
@crossdomain(origin=origin)
def addPortfolio():
    ack = dbio.addPortfolio( request[ constants.CLIENT_NAME ], request[ constants.PORTFOLIO_NAME ] );
    return ack;

if __name__ == '__main__':
    app.run();