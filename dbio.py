from pymongo import MongoClient
import constants

def dictFilter( d, keys ):
    return( {k: v for k, v in d.items() if k in keys } )

# example schemeCode = "101671"
def fundNav( client, schemeCode ):
    data = client.fundData( { constants.SCHEMECODE_KEY : schemeCode } )
    if( data.count() == 1 ):
        dates = data[0][ constants.NAV_DATES_KEY ];
        values = [ float( i ) for i in data[0][ constants.NAV_VALUES_KEY ] ];
        nav = { constants.DATES_KEY : dates, constants.VALUES_KEY : values };
    else:
        nav = { constants.DATES_KEY : [], constants.VALUES_KEY : [] };
    return( nav );

def fundSchemes( client ):
    schemeCols = dict( [ (key,1) for key in constants.SCHEME_ATTRIBUTES ] );
    schemeCols[ constants.MONGO_ID ] = 0;
    data = client.fundData( {}, schemeCols );
    return( [ scheme for scheme in data ] );