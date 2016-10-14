from investment import Investment
import dbclient
import constants
import pandas as pd

class Fund(Investment):
    schemeCode=None # example schemeCode = "101671"
    client=None # db client

    def __init__(self,schemeCode,client):
        self.schemeCode = schemeCode
        self.client = client

    def nav( self ):
        data = self.client.fundData( { constants.SCHEMECODE_KEY : self.schemeCode } )
        if( data.count() == 1 ):
            dates = data[0][ constants.NAV_DATES_KEY ]
            values = [ float( i ) for i in data[0][ constants.NAV_VALUES_KEY ] ]
            nav = pd.Series( values, dates ).sort_index()
        else:
            nav = pd.Series( [], [] )
        return( nav )

    def schemeInfo( self ):
        schemeCols = dict( [ (key,1) for key in constants.SCHEME_ATTRIBUTES ] );
        schemeCols[ constants.MONGO_ID ] = 0;
        data = self.client.fundData( { constants.SCHEMECODE_KEY : self.schemeCode }, schemeCols );
        if( data.count() == 1 ):
            data = data[0]
        else:
            data = {}
        return( data )
