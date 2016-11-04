from flask import Blueprint, request
import dbio
import dbclient
import constants
from utils import json
import utils
from portfolio import Portfolio

portfolio_api = Blueprint('portfolio_api',__name__)
client = dbclient.MClient()

@portfolio_api.route('/client/<clientName>')
def getClientPortfolios( clientName ):
    return json( dbio.clientPortfolios( client, clientName ) )

@portfolio_api.route('/<portfolioId>')
def getPortfolio( portfolioId ):
    return json( Portfolio( portfolioId, client ).portfolioData() )

@portfolio_api.route('/<portfolioId>/transactions')
def getPortfolioTransactions( portfolioId ):
    return json( Portfolio( portfolioId, client ).transactions() )

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

@portfolio_api.route('/<portfolioId>/nav')
def portfolioNav( portfolioId ):
    return( json( utils.ts2dict( Portfolio( portfolioId, client ).nav() ) ) )

@portfolio_api.route('/<portfolioId>/return/<window>')
def portfolioReturn( portfolioId, window ):
    return( json( utils.ts2dict( Portfolio( portfolioId, client ).rollingReturn( window ) ) ) )

@portfolio_api.route('/<portfolioId>/return-stats')
def portfolioReturnStats( portfolioId ):
    return( json( Portfolio( portfolioId, client ).returnStats() ) )