from pymongo import MongoClient

class MClient():
    def __init__( self ):
        client = MongoClient();
        self.fundDb = client.fund_db;
        self.fundDataColl = self.fundDb.fund_data;
    
    def fundData( self, searchCondition, keys={} ):
        if( len( keys ) == 0 ):
            return self.fundDataColl.find( searchCondition );
        else:
            return self.fundDataColl.find( searchCondition, keys );