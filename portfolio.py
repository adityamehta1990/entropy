import dbclient
import constants
import datetime
import pandas as pd
from fund import Fund
from investment import Investment

# todo : replace all strings with constants

class Portfolio(Investment):
    portfolioId=None
    client=None
    
    # we can store portfolio data here and use it directly
    # if someone passes an invalid portfolioId, that can be caught in __init__

    def __init__(self,portfolioId,client):
        self.portfolioId=portfolioId
        self.client=client

    def portfolioData(self):
        data = self.client.portfolioData( { constants.PORTFOLIO_ID : self.portfolioId }, { constants.TRANSACTIONS : 0 } );
        if( data.count() == 1 ):
            P = data[0]
        else:
            P = {}
        return( P )

    def transactions(self):
        data = self.client.portfolioData( { constants.PORTFOLIO_ID : self.portfolioId } );
        if( data.count() == 1 ):
            Ts = data[0][ constants.TRANSACTIONS ]
        else:
            Ts = []
        return( Ts )
    
    def aggregateTxns(self):
        txns = pd.DataFrame( self.transactions() )
        # first aggregate qty and cf by date+schemeCode to handle multiple txns on a date
        aggTxns = txns.groupby(by=['date','schemeCode']).agg({'cashflow':sum,'quantity':sum})
        cumAggTxns = aggTxns.groupby(level='schemeCode').cumsum().rename(columns={'cashflow':'cum_cashflow','quantity':'cum_quantity'})
        # concat cum by index and reset to date index
        return pd.concat([aggTxns,cumAggTxns],axis=1).reset_index(level='schemeCode')

    def nav(self):
        aggTxns = self.aggregateTxns()
        qty = aggTxns.pivot(columns='schemeCode',values='cum_quantity')
        # generate empty nav curve from first txn to today
        index = pd.DatetimeIndex( freq='D',start=qty.first_valid_index(),end=datetime.datetime.today() )
        nav = pd.Series(index=index).fillna(0)
        for (schemeCode,schemeQty) in qty.iteritems():
            schemeNav = Fund(schemeCode,self.client).nav()
            # dont fillna here, if fund nav is missing, it should yield NaN
            nav = nav.add(schemeQty.reindex(schemeNav.index,method='pad') * schemeNav)
        return(nav.dropna())
    
    def cashflow(self):
        aggTxns = self.aggregateTxns()
        return pd.Series(aggTxns.groupby(level='date').sum().cum_cashflow)