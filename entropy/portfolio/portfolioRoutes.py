from flask import Blueprint
from flask import request
from entropy.db import dbclient
from entropy.utils import utils
from entropy.portfolio import portfolioData
from entropy.portfolio.portfolio import Portfolio

portfolio_api = Blueprint('portfolio_api',__name__)
client = dbclient.MClient()

@portfolio_api.route('/client/<clientName>')
def getClientPortfolios(clientName):
    return utils.json(portfolioData.clientPortfolios(client, clientName))

@portfolio_api.route('/<portfolioId>')
def getPortfolio( portfolioId ):
    return utils.json(Portfolio(portfolioId, client).portfolioData())

@portfolio_api.route('/new',methods=['POST'])
def addPortfolio():
    clientName = request[portfolioData.CLIENT_NAME].strip()
    portfolioName = request[portfolioData.PORTFOLIO_NAME].strip()
    ack = portfolioData.addPortfolio(client, clientName, portfolioName)
    return utils.json(ack)

@portfolio_api.route('/<portfolioId>/transactions')
def getPortfolioTransactions(portfolioId):
    return utils.json(Portfolio(portfolioId, client).transactions())

@portfolio_api.route('/<portfolioId>/transaction/new',methods=['POST'])
def addTransaction(portfolioId):
    data = request.get_json()
    ack = portfolioData.addTransaction(client, portfolioId, data[portfolioData.ASSET_CODE],
        data[portfolioData.ASSET_NAME], data[portfolioData.TXN_CASHFLOW],
        data[portfolioData.TXN_QUANTITY], utils.dateParser(data[portfolioData.TXN_DATE]))
    return utils.json(ack)

@portfolio_api.route('/<portfolioId>/transaction/<transactionId>',methods=['DELETE'])
def removeTransaction(portfolioId, transactionId):
    # todo: add elif for PUT (Modify)
    if request.method == 'DELETE':
        ack = dbio.removeTransaction(client, portfolioId, int(transactionId))
        return utils.json(ack)

@portfolio_api.route('/<portfolioId>/nav')
def portfolioNav(portfolioId):
    return utils.json(utils.ts2dict(Portfolio(portfolioId, client).nav()))

@portfolio_api.route('/<portfolioId>/return/<window>')
def portfolioReturn(portfolioId, window):
    return utils.json(utils.ts2dict(Portfolio(portfolioId, client).rollingReturn(window)))

@portfolio_api.route('/<portfolioId>/return-stats')
def portfolioReturnStats(portfolioId):
    return utils.json(Portfolio(portfolioId, client).returnStats())
