from flask import Blueprint
from flask import request
from entropy.db import dbclient
import entropy.utils.dateandtime as dtu
import entropy.utils.webio as webio
from entropy.portfolio import portfolioData
from entropy.portfolio.portfolio import Portfolio

portfolio_api = Blueprint('portfolio_api', __name__)
client = dbclient.MClient()

@portfolio_api.route('/client/<clientName>')
def getClientPortfolios(clientName):
    return webio.json(portfolioData.clientPortfolios(client, clientName))

@portfolio_api.route('/<portfolioId>')
def getPortfolio(portfolioId):
    return webio.json(Portfolio(portfolioId, client).portfolioData())

@portfolio_api.route('/new', methods=['POST'])
def addPortfolio():
    clientName = request[portfolioData.CLIENT_NAME].strip()
    portfolioName = request[portfolioData.PORTFOLIO_NAME].strip()
    ack = portfolioData.addPortfolio(client, clientName, portfolioName)
    return webio.json(ack)

@portfolio_api.route('/<portfolioId>/transactions')
def getPortfolioTransactions(portfolioId):
    return webio.json(Portfolio(portfolioId, client).transactions())

@portfolio_api.route('/<portfolioId>/transaction/new', methods=['POST'])
def addTransaction(portfolioId):
    data = request.get_json()
    ack = portfolioData.addTransaction(client, portfolioId, data[portfolioData.ASSET_CODE],
        data[portfolioData.ASSET_NAME], data[portfolioData.TXN_CASHFLOW],
        data[portfolioData.TXN_QUANTITY], dtu.dateParser(data[portfolioData.TXN_DATE]))
    return webio.json(ack)

@portfolio_api.route('/<portfolioId>/transaction/<transactionId>', methods=['DELETE'])
def removeTransaction(portfolioId, transactionId):
    # todo: add elif for PUT (Modify)
    if request.method == 'DELETE':
        ack = portfolioData.removeTransaction(client, portfolioId, int(transactionId))
        return webio.json(ack)

@portfolio_api.route('/<portfolioId>/nav')
def portfolioNav(portfolioId):
    return webio.json(webio.ts2dict(Portfolio(portfolioId, client).nav()))

@portfolio_api.route('/<portfolioId>/return/<window>')
def portfolioReturn(portfolioId, window):
    return webio.json(webio.ts2dict(Portfolio(portfolioId, client).rollingReturn(window)))

@portfolio_api.route('/<portfolioId>/return-stats')
def portfolioReturnStats(portfolioId):
    return webio.json(Portfolio(portfolioId, client).returnStats())
