from pymongo import MongoClient
import constants

def dictFilter( d, keys ):
    return( {k: v for k, v in d.items() if k in keys } )

def fundDb( client ):
    return client.fund_db;

def fundMetaData( db ):
    return db.fund_meta_data;

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
    coll = fundMetaData( db );
    client.close();
    data = coll.find();
    return( [ scheme for scheme in data ] );