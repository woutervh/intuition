# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  Benchmark loader modified to allow live data streaming
  ------------------------------------------------------

  :copyright (c) 2014 Xavier Bruhiere.
  :license: Apache2.0, see LICENSE for more details.
'''


from datetime import datetime
import pandas as pd
from collections import OrderedDict
import zipline.data.loader as zipline
import intuition.data.data as data


class LiveBenchmark(object):
    def __init__(self, end, frequency='daily', loopback=4):
        self.last_trading_day = end
        self.loopback = loopback
        if frequency == 'minute':
            self.offset = pd.datetools.Minute()
        elif frequency == 'daily':
            self.offset = pd.datetools.Day()
        else:
            raise NotImplementedError()

    def normalize_date(self, test_date):
        ''' Same function as zipline.finance.trading.py'''
        test_date = pd.Timestamp(test_date, tz='UTC')
        return pd.tseries.tools.normalize_date(test_date)

    def surcharge_market_data(self, bm_symbol='^GSPC'):
        #TODO Parametric
        #event_dt = datetime.today().replace(tzinfo=pytz.utc)
        event_dt = self.normalize_date(datetime.now())

        #TODO Handle invalid code
        for exchange, infos in data.Exchanges.iteritems():
            if infos['symbol'] == bm_symbol:
                code = data.Exchanges[exchange]['code']
                break

        bm_returns, tr_curves = zipline.load_market_data(bm_symbol)

        dates = pd.date_range(event_dt,
                              periods=len(bm_returns))
        #NOTE What is tr_curves['tid'] ?
        #TODO Replace values to detect the fake later
        tr_fake = OrderedDict(sorted(
            ((pd.Timestamp(event_dt + i*self.offset), c)
             for i, c in enumerate(tr_curves.values())),
            key=lambda t: t[0]))

        bm_fake = pd.Series([code] * len(dates), index=dates)
        for i, dt in enumerate(tr_curves.keys()):
            pd.Timestamp(event_dt + i * self.offset)

        return bm_fake, tr_fake