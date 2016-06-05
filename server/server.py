from flask import Flask, jsonify
import dbio
import analytics
import constants
import dbclient

app = Flask(__name__);
client = dbclient.MClient();

def json( data ):
    return( jsonify( { constants.JSON_KEY : data } ) );

@app.route('/fund-data/nav/<schemeCode>')
def getFundNav( schemeCode ):
    return json( dbio.fundNav( client, schemeCode ) );

@app.route('/fund-data/return/<schemeCode>/<window>')
def getFundReturn( schemeCode, window ):
    return json( analytics.fundReturn( client, schemeCode, window ) );

@app.route('/fund-data/schemes')
def getFundSchemes():
    return json( dbio.fundSchemes( client ) );

if __name__ == '__main__':
    app.run();