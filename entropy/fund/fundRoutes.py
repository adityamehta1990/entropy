from flask import Blueprint
from flask import request
from entropy.db import dbclient
import entropy.utils.dateandtime as dtu
import entropy.utils.webio as webio
from entropy.fund.fund import Fund
from entropy.fund import fundData

fund_api = Blueprint('fund_api',__name__)
client = dbclient.MClient()

# fund Page
@fund_api.route('/funds')
def getFundList():
    return webio.json(fundData.fundList(client))

@fund_api.route('/funds/<navDate>')
def getFundListOnDate(navDate):
    return webio.json(fundData.fundList(client, dtu.dateParser(navDate)))

@fund_api.route('/fund/<Id>', methods=['GET'])
def getFundInfo(Id):
    return webio.json(Fund(Id,client).fundInfo())

@fund_api.route('/enriched/<Id>')
def enrichedFundInfo(Id):
    return webio.json(fundData.enrichedFundInfo(client, Id))

@fund_api.route('/fund/<Id>', methods=['POST'])
def updateFundInfo(Id):
    fundInfo = request.get_json()
    return webio.json(fundData.updateFundInfo(client, Id, fundInfo))

@fund_api.route('/nav/<Id>')
def getFundNav(Id):
    return webio.json(webio.ts2dict(Fund(Id, client).nav()))

@fund_api.route('/return/<Id>/<window>')
def getFundReturn(Id, window):
    return webio.json(webio.ts2dict(Fund(Id, client).rollingReturn(window)))
