from flask import Blueprint
import dbio
import dbclient
from utils import json
import utils
from fund import Fund

fund_api = Blueprint('fund_api',__name__)
client = dbclient.MClient()

# fund Page
@fund_api.route('/schemes')
def getFundSchemes():
    return json( dbio.fundSchemes( client ) )

@fund_api.route('/schemes/<navDate>')
def getFundSchemesForDate( navDate ):
    return json( dbio.fundSchemes( client, utils.dateParser( navDate ) ) )

@fund_api.route('/scheme/<schemeCode>')
def getFundScheme( schemeCode ):
    return json( Fund( schemeCode, client ).schemeInfo() )

@fund_api.route('/nav/<schemeCode>')
def getFundNav( schemeCode ):
    return json( utils.ts2dict( Fund( schemeCode, client ).nav() ) )

@fund_api.route('/return/<schemeCode>/<window>')
def getFundReturn( schemeCode, window ):
    return json( utils.ts2dict( Fund( schemeCode, client ).rollingReturn( window ) ) )
