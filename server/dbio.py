from pymongo import MongoClient
import constants

def dictFilter( d, keys ):
    return( {k: v for k, v in d.items() if k in keys } )

def fundDb( client ):
    return client.fund_db;

def fundData( db ):
    return db.fund_data;

# example schemeCode = "101671"
def fundNav( schemeCode ):
    client = MongoClient();
    db = fundDb(client);
    coll = fundData( db );
    client.close();
    data = coll.find( { constants.SCHEMECODE_KEY : schemeCode } )
    if( data.count() == 1 ):
        dates = data[0][ constants.NAV_DATES_KEY ];
        values = [ float( i ) for i in data[0][ constants.NAV_VALUES_KEY ] ];
        nav = { constants.DATES_KEY : dates, constants.VALUES_KEY : values };
    else:
        nav = { constants.DATES_KEY : [], constants.VALUES_KEY : [] };
    return( nav );

def fundSchemes():
    client = MongoClient();
    db = fundDb( client );
    coll = fundData( db );
    client.close();
    schemeCols = dict( [ (key,1) for key in constants.SCHEME_ATTRIBUTES ] );
    schemeCols[ constants.MONGO_ID ] = 0;
    data = coll.find({},schemeCols );
    return( dict( [ (scheme[constants.SCHEMECODE_KEY],scheme) for scheme in data ] ) );