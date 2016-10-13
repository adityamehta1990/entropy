from flask import Blueprint, request
import dbio
import dbclient
import constants
from utils import json
import utils

portfolio_api = Blueprint('portfolio_api',__name__)
client = dbclient.MClient()

@portfolio_api.route('/client/<clientName>')
def getClientPortfolios( clientName ):
    return json( dbio.clientPortfolios( client, clientName ) )

@portfolio_api.route('/<portfolioId>')
def getPortfolio( portfolioId ):
    return json( dbio.portfolioData( client, portfolioId ) )

@portfolio_api.route('/<portfolioId>/transactions')
def getPortfolioTransactions( portfolioId ):
    return json( dbio.transactions( client, portfolioId ) )

@portfolio_api.route('/new',methods=['POST'])
def addPortfolio():
    ack = dbio.addPortfolio( client, request[ constants.CLIENT_NAME ], request[ constants.PORTFOLIO_NAME ] )
    return json( ack )

@portfolio_api.route('/<portfolioId>/transaction/new',methods=['POST'])
def addTransaction( portfolioId ):
    data = request.get_json()
    ack = dbio.addTransaction( client, portfolioId, data[ constants.ASSET_CODE ], data[ constants.ASSET_NAME ],
        data[ constants.TXN_CASHFLOW ], data[ constants.TXN_QUANTITY ], utils.dateParser( data[ constants.TXN_DATE ] ) )
    return json( ack )

@portfolio_api.route('/<portfolioId>/transaction/<transactionId>',methods=['DELETE'])
def removeTransaction( portfolioId, transactionId ):
    # todo: add elif for PUT (Modify)
    if request.method == 'DELETE':
        ack = dbio.removeTransaction( client, portfolioId, int(transactionId) )
        return( json( ack ) )
