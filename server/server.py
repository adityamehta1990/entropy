from flask import Flask, jsonify
import dbio

app = Flask(__name__)

@app.route('/fund-data/<schemeCode>')
def getFundNav( schemeCode ):
    return jsonify( dbio.fundNav( schemeCode ) );

if __name__ == '__main__':
    app.run();