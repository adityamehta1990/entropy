from entropy.investment import Investment
from entropy.fund import fundData
import entropy.db.dbclient
import pandas as pd
import re

# todo: move these to fundData/fundio
# should not edit these attrs
SCHEME_ATTRIBUTES_RAW = ['schemeName', 'schemeCode', 'schemeType', 'managerName']
# derived from raw
SCHEME_ATTRIBUTES_CALC = ['fundName', 'isOpenEnded', 'hasDividend', 'dividendPeriod', 'isDirect']
# attrs input from tool because they are not raw or cannot be derived
SCHEME_ATTRIBUTES_CLASSIFICATION = {
    'assetClass' : ['equity', 'debt', 'hybrid']
    #'strategy': # large cap/long term/liquid
}
SCHEME_ATTRIBUTES_EQUITY = {
    'marketCap' : ['large', 'medium', 'small'],
    'investmentStyle' : ['value', 'growth', 'blend'],
    'sector' : ['multi'] # multi if no sector
}
SCHEME_ATTRIBUTES_DEBT = {
    'duration' : ['short', 'medium', 'long'],
    'creditQuality' :  ['high', 'medium', 'low'],
    'underlier' : ['gilt', 'corp', 'liquid']
}
SCHEME_ATTRIBUTES_INPUT = SCHEME_ATTRIBUTES_CALC + list(SCHEME_ATTRIBUTES_CLASSIFICATION.keys()) + \
                    list( SCHEME_ATTRIBUTES_EQUITY.keys() ) + list( SCHEME_ATTRIBUTES_DEBT.keys() )
SCHEME_ATTRIBUTES = SCHEME_ATTRIBUTES_RAW + SCHEME_ATTRIBUTES_INPUT

SCHEME_CODE_KEY = 'schemeCode'
NAV_DATES_KEY = 'navDates'
NAV_VALUES_KEY = 'nav'
SCHEME_RETURN_OPTION_IDENTIFIERS = ['GROWTH','DIVIDEND']
SCHEME_INVESTMENT_OPTION_IDENTIFIERS = ['DIRECT','REGULAR']

class Fund(Investment):
    idStr=None # MONGO_ID for this fund
    client=None # db client

    def __init__(self,idStr,client):
        self.client = client
        self._id = self._id

    def nav( self ):
        return fundData.fundNAV(self.client, self._id)

    # can implement dividend into this
    # for now, cashflow for fund is empty
    def cashflow(self):
        return pd.Series([],[])

    def schemeInfo( self ):
        return fundData.fundInfo(self.client, self._id)

    # only enrich missing data
    def enrichedSchemeInfo( self ):
        info = self.schemeInfo()
        enrichedInfo = {}
        nameParts = [ part.strip() for part in info['schemeName'].split('-') ]

        if not info.get('fundName'):
            pattern = re.compile('|'.join(SCHEME_RETURN_OPTION_IDENTIFIERS + SCHEME_INVESTMENT_OPTION_IDENTIFIERS),re.IGNORECASE)
            enrichedInfo['fundName'] = '-'.join( filter( lambda x: not pattern.search(x), nameParts ) )
        
        if not info.get('isOpenEnded'):
            enrichedInfo['isOpenEnded'] = re.compile('open ended scheme',re.IGNORECASE).search(info['schemeType']) is not None
        
        if not info.get('isDirect'):
            enrichedInfo['isDirect'] = re.compile('direct',re.IGNORECASE).search(info['schemeName']) is not None
        
        if not info.get('hasDividend'):
            enrichedInfo['hasDividend'] = re.compile('dividend',re.IGNORECASE).search(info['schemeName']) is not None
        
        return( enrichedInfo )