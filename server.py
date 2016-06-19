from flask import Flask, jsonify
import dbio
import analytics
import constants
import dbclient
from crossdomain import *

app = Flask(__name__);
client = dbclient.MClient();
origin = '*';

def json( data ):
    return( jsonify( { constants.JSON_KEY : data } ) );

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

if __name__ == '__main__':
    app.run();