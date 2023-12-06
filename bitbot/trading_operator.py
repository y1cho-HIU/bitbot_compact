import asyncio
import datetime
import json
import pprint
import statistics

import data_getter
import strategy


class Operator:
    POS_OUT = 0
    POS_LONG = 1
    POS_SHORT = -1

    def __init__(self, client_info, sma_period, env_weight, rrr_rate, symbol='XRPUSDT'):
        self.client = client_info
        self.dataGetter = data_getter.DataGetter(client_info=client_info, sma_period=sma_period, symbol=symbol)
        self.strategy = strategy.Strategy(sma_period=sma_period, env_weight=env_weight, rrr_rate=rrr_rate)

        self.coin_data = self.dataGetter.get_info_period()  # LIST
        self.now_position = self.POS_OUT
        self.next_position = self.POS_OUT
        self.signal = False
        self.start_time = None
        self.start_balance = None
        self.init_balance = None
        self.symbol = symbol
        self.sma_period = sma_period
        self.env_weight = env_weight
        self.rrr_rate = rrr_rate

    def calc_quantity(self, side, close=False):
        # get available balance
        # get bid and ask price
        # calc (avb * 0.9) / bid or ask price
        market_price = self.client.get_ticker(symbol=self.symbol)
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
        order = None
        if self.now_position == self.POS_OUT:
            if self.next_position == self.POS_LONG:
                """ OUT -> LONG """
                order = self.client.futures_create_order(symbol=self.symbol,
                                                         type='MARKET',
                                                         side='BUY',
                                                         quantity=self.calc_quantity('BUY'))
                self.now_position = self.POS_LONG
                print('##### OUT -> LONG #####')
            elif self.next_position == self.POS_SHORT:
                """ OUT -> SHORT """
                order = self.client.futures_create_order(symbol=self.symbol,
                                                         type='MARKET',
                                                         side='SELL',
                                                         quantity=self.calc_quantity('SELL'))
                self.now_position = self.POS_SHORT
                print('##### OUT -> SHORT #####')
        elif self.now_position == self.POS_LONG and self.next_position == self.POS_OUT:
            """ LONG -> OUT """
            order = self.client.futures_create_order(symbol=self.symbol,
                                                     type='MARKET',
                                                     side='SELL',
                                                     quantity=self.calc_quantity('SELL', close=True),
                                                     reduceOnly=True)
            self.now_position = self.POS_OUT
            print('##### LONG -> OUT #####')
        elif self.now_position == self.POS_SHORT and self.next_position == self.POS_OUT:
            """ SHORT -> OUT """
            order = self.client.futures_create_order(symbol=self.symbol,
                                                     type='MARKET',
                                                     side='BUY',
                                                     quantity=self.calc_quantity('BUY', close=True),
                                                     reduceOnly=True)
            self.now_position = self.POS_OUT
            print('##### SHORT -> OUT #####')

        self.strategy.set_now_position(self.next_position)
        if order is not None:
            print(order)

    def terminate_position(self):
        """ if quit-cmd entered. """
        order = None
        pos_info = self.client.futures_position_information
        if self.now_position == self.POS_LONG:
            order = self.client.futures_create_order(symbol=self.symbol,
                                                     type='MARKET',
                                                     side='SELL',
                                                     quantity=float(pos_info[0]['positionAmt']),
                                                     reduceOnly=True)
        elif self.now_position == self.POS_SHORT:
            order = self.client.futures_create_order(symbol=self.symbol,
                                                     type='MARKET',
                                                     side='BUY',
                                                     quantity=abs(float(pos_info[0]['positionAmt'])),
                                                     reduceOnly=True)
        if order is not None:
            print(order)

    def make_coin_data(self):
        now_data = self.dataGetter.get_info()
        print(now_data)
        if len(self.coin_data) < self.sma_period:
            self.coin_data.append(now_data)
        elif len(self.coin_data) == self.sma_period:
            del self.coin_data[0]
            self.coin_data.append(now_data)

    async def execute_trading(self):
        self.start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.init_balance = self.client.futures_account()['availableBalance']
        print(f'START TIME \t: {self.start_time}')
        print(f'INIT BALANCE \t: {self.init_balance}')
        try:
            while True:
                self.make_coin_data()
                self.signal, self.next_position = self.strategy.envelope_strategy(coin_data=self.coin_data)
                if self.signal is True:
                    self.trading_order()
                self.update_json_info()
                await asyncio.sleep(300)
        except Exception as e:
            print(f'ERROR {e}')

    async def cmd_input(self):
        while True:
            key = await asyncio.get_event_loop().run_in_executor(None, input, "cmd (press h or help)> ")
            # help command
            if key == "help" or key == "h":
                self.display_help_cmd()
            # overall information
            if key == "info" or key == "i":
                print("** OVERALL INFO **")
                pprint.pprint(self.get_all_info())
            # coin data
            if key == "coin" or key == "c":
                print("** COIN DATA **")
                pprint.pprint(self.coin_data)
                print("** BOOK DATA **")
                print(self.dataGetter.get_book_info())
            # statistics info
            if key == "stat" or key == "s":
                print("** STATISTICS INFO **")
                pprint.pprint(self.get_statistics_info())
            if key == "position" or key == "p":
                print("** POSITION INFO **")
                print(self.client.futures_position_information(symbol=self.symbol))
            if key == "trade" or key == "t":
                print("** TRADING INFO **")
                pprint.pprint(self.get_trading_info())
            # quit cmd
            elif key == "quit" or key == "q":
                self.terminate_position()
                print("** SUCCESSFULLY TERMINATED. **")
                pprint.pprint(self.get_all_info())
                print("="*20)
                pprint.pprint(self.get_trading_info())
                # log trading_info
                asyncio.get_event_loop().stop()

    @staticmethod
    def display_help_cmd():
        print("############# help cmd #############")
        print("display all info \t\t --press info or i")
        print("display coin data \t\t --press coin or c")
        print("display statistics \t\t --press stat or s")
        print("display position \t\t --press position or p")
        print("display trading info \t\t --press trade or t")
        print("quit command \t\t\t --press quit or q")

    def get_total_profit(self):
        trades = self.client.futures_account_trades(symbol=self.symbol, limit=100)
        total_profit = 0.0
        total_cost = 0.0

        for trade in trades:
            # time = datetime.datetime.utcfromtimestamp(trade['time'] / 1000).strftime("%Y-%m-%d %H:%M:%S")
            price = float(trade['price'])
            qty = float(trade['qty'])
            commission = float(trade['commission'])

            if trade['buyer']:
                total_cost += qty * price + commission
            else:
                total_profit += qty * price - commission

        pnl = total_profit - total_cost
        pnl_percentage = pnl / total_cost * 100 if total_cost != 0 else 0.0

        return {
            "total_profit": round(total_profit, 2),
            "total_cost": round(total_cost, 2),
            "pnl": round(pnl, 2),
            "pnl_percentage": round(pnl_percentage, 4)
        }

    def get_position_info(self):
        pos_info = self.client.futures_position_information(symbol=self.symbol)
        pos_side = "OUT"
        if float(pos_info[0]['positionAmt']) > 0:
            pos_side = "LONG"
        elif float(pos_info[0]['positionAmt']) < 0:
            pos_side = "SHORT"

        return {
            "position": pos_side,
            "positionAmt": abs(float(pos_info[0]['positionAmt']))
        }

    def get_statistics_info(self):
        close_list = [data['close'] for data in self.coin_data]
        now_price = self.coin_data[-1]['close']
        sma = round(sum(close_list) / len(close_list), 6)
        std_dev = round(statistics.stdev(close_list), 6)
        env_up = round(sma + (std_dev * self.env_weight), 6)
        env_down = round(sma - (std_dev * self.env_weight), 6)
        rrr_up = round(env_up + (env_up - sma) / self.rrr_rate, 6)
        rrr_down = round(env_down - (sma - env_down) / self.rrr_rate, 6)

        return {"now_price": now_price,
                "now_sma": sma,
                "std_dev": std_dev,
                "env_up": env_up,
                "env_down": env_down,
                "rrr_up": rrr_up,
                "rrr_down": rrr_down}

    def get_all_info(self):
        # get all info as json_style
        return {"symbol": self.symbol,
                "init_balance": round(self.init_balance, 2),
                "now_balance": self.client.futures_account()['availableBalance'],
                "total_profit": round(self.get_total_profit(), 2),
                "7d_profit": "float",
                "1d_profit": "float",
                "start_time": self.start_time,
                "now_pos": self.get_position_info(),
                }

    def get_trading_info(self):
        return {"trading_info": self.client.futures_account_trades(symbol=self.symbol)}

    def update_json_info(self):
        """
        modifying time : strf

        coin_data.json
        overall_info.json
        trading_info.json
        """
        coin_data_file_path = "json_repository/coin_data.json"
        overall_info_file_path = "json_repository/overall_info.json"
        trading_info_file_path = "json_repository/trading_info.json"
        stat_info_file_path = "json_repository/statistics_info.json"

        with open(coin_data_file_path, 'w') as coin:
            json.dump(self.coin_data, coin, indent=4)

        with open(overall_info_file_path, 'w') as ova:
            json.dump(self.get_all_info(), ova, indent=4)

        with open(trading_info_file_path, 'w') as trade:
            json.dump(self.get_trading_info(), trade, indent=4)

        with open(stat_info_file_path, 'w') as stat:
            json.dump(self.get_statistics_info(), stat, indent=4)
