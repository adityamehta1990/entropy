from flask import Blueprint
import dbio
import dbclient
import analytics
from utils import json
import utils

fund_api = Blueprint('fund_api',__name__)
client = dbclient.MClient()

# fund Page
@fund_api.route('/nav/<schemeCode>')
def getFundNav( schemeCode ):
    return json( dbio.fundNav( client, schemeCode ) )

@fund_api.route('/return/<schemeCode>/<window>')
def getFundReturn( schemeCode, window ):
    return json( analytics.fundReturn( client, schemeCode, window ) )

@fund_api.route('/schemes')
def getFundSchemes():
    return json( dbio.fundSchemes( client ) )

@fund_api.route('/schemes/<navDate>')
def getFundSchemesForDate( navDate ):
    return json( dbio.fundSchemes( client, utils.dateParser( navDate ) ) )

@fund_api.route('/scheme/<schemeCode>')
def getFundScheme( schemeCode ):
    return json( dbio.fundScheme( client, schemeCode ) )
