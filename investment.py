import analytics

# base class for any type of investment - portfolio, fund, etc
# this can implement common analytics for returns and risk

# make this abstract
class Investment:
    def returnStats(self):
        # this should give various period returns (YTD, MTD, 1y, 3y, SI, etc)
        pass

    def rollingReturn(self,window):
        return analytics.tsreturn(self.nav(),window)