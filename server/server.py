from flask import Flask, jsonify
import dbio
import analytics
import constants

app = Flask(__name__)

def json( data ):
    return( jsonify( { constants.JSON_KEY : data } ) );

@app.route('/fund-data/nav/<schemeCode>')
def getFundNav( schemeCode ):
    return json( dbio.fundNav( schemeCode ) );

@app.route('/fund-data/return/<schemeCode>/<window>')
def getFundReturn( schemeCode, window ):
    return json( analytics.fundReturn( schemeCode, window ) );

@app.route('/fund-data/schemes')
def getFundSchemes():
    return json( dbio.fundSchemes() );

if __name__ == '__main__':
    app.run();