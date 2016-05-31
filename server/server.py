from flask import Flask, jsonify
import dbio
import analytics

app = Flask(__name__)

@app.route('/fund-data/nav/<schemeCode>')
def getFundNav( schemeCode ):
    return jsonify( dbio.fundNav( schemeCode ) );

@app.route('/fund-data/return/<schemeCode>/<window>')
def getFundReturn( schemeCode, window ):
    return jsonify( analytics.fundReturn( schemeCode, window ) );

@app.route('/fund-data/schemes')
def getFundSchemes():
    return jsonify( dbio.fundSchemes() );

if __name__ == '__main__':
    app.run();