from binance.client import Client

import data_getter


class Account:
    POS_OUT = 0
    POS_LONG = 1
    POS_SHORT = -1

    def __init__(self, client_info, sma_period, symbol='XRPUSDT'):
        self.client = client_info   # client_info = Client(api_key, api_secret)
        self.dataGetter = data_getter.DataGetter(client_info=client_info, sma_period=sma_period, symbol=symbol)

        self.symbol = symbol
        self.now_position = self.POS_OUT
        self.next_position = self.POS_OUT

    def calc_quantity(self, side, close=False):
        # get available balance
        # get bid and ask price
        # calc (avb * 0.9) / bid or ask price
        market_price = self.dataGetter.get_book_info()
        account_info = self.client.futures_account()
        free_balance = float(account_info['availableBalance'])
        position_info = self.client.futures_position_information(symbol=self.symbol)

        if side == 'BUY':
            if close is True:
                return abs(float(position_info[0]['positionAmt']))
            else:
                return round((free_balance * 0.9) / float(market_price['bidPrice']), 4)
        elif side == 'SELL':
            if close is True:
                return abs(float(position_info[0]['positionAmt']))
            else:
                return round((free_balance * 0.9) / float(market_price['askPrice']), 4)

    def trading_order(self):
        if self.now_position == self.POS_OUT:
            if self.next_position == self.POS_LONG:
                """ OUT -> LONG """
                order = self.client.futures_create_order(symbol=self.symbol,
                                                         type='MARKET',
                                                         side='BUY',
                                                         quantity=self.calc_quantity('BUY'))
                self.now_position = self.POS_LONG
                print('##### OUT -> LONG #####')
                print(order)
            elif self.next_position == self.POS_SHORT:
                """ OUT -> SHORT """
                order = self.client.futures_create_order(symbol=self.symbol,
                                                         type='MARKET',
                                                         side='SELL',
                                                         quantity=self.calc_quantity('SELL'))
                self.now_position = self.POS_SHORT
                print('##### OUT -> SHORT #####')
                print(order)
        elif self.now_position == self.POS_LONG and self.next_position == self.POS_OUT:
            """ LONG -> OUT """
            order = self.client.futures_create_order(symbol=self.symbol,
                                                     type='MARKET',
                                                     side='SELL',
                                                     quantity=self.calc_quantity('SELL', close=True),
                                                     reduceOnly=True)
            self.now_position = self.POS_OUT
            print('##### LONG -> OUT #####')
            print(order)
        elif self.now_position == self.POS_SHORT and self.next_position == self.POS_OUT:
            """ SHORT -> OUT """
            order = self.client.futures_create_order(symbol=self.symbol,
                                                     type='MARKET',
                                                     side='BUY',
                                                     quantity=self.calc_quantity('BUY', close=True),
                                                     reduceOnly=True)
            self.now_position = self.POS_OUT
            print('##### SHORT -> OUT')
            print(order)

    def get_account_info(self):
        return self.client.futures_account()

    def get_position_info(self):
        return self.client.futures_position_information(symbol=self.symbol)

    def get_trading_info(self):
        return self.client.futures_account_trades(symbol=self.symbol)

    def get_profit_info(self):
        print("not yet.")