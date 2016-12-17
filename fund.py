from investment import Investment
import dbclient
import constants
import pandas as pd
import re

# we get raw data from amfi, which can be parsed to enrich meta data about a fund

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
    schemeCode=None # example schemeCode = "101671"
    client=None # db client

    def __init__(self,schemeCode,client):
        self.schemeCode = schemeCode
        self.client = client

    def nav( self ):
        data = self.client.fundData( { SCHEME_CODE_KEY : self.schemeCode } )
        if( data.count() == 1 ):
            dates = data[0][ NAV_DATES_KEY ]
            values = [ float( i ) for i in data[0][ NAV_VALUES_KEY ] ]
            nav = pd.Series( values, dates ).sort_index()
        else:
            nav = pd.Series( [], [] )
        return( nav )

    # can implement dividend into this
    # for now, cashflow for fund is empty
    def cashflow(self):
        return pd.Series([],[])

    def schemeInfo( self ):
        schemeCols = dict( [ (key,1) for key in SCHEME_ATTRIBUTES ] );
        data = self.client.fundData( { SCHEME_CODE_KEY : self.schemeCode }, schemeCols );
        if( data.count() == 1 ):
            data = data[0]
        else:
            data = {}
        return( data )

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