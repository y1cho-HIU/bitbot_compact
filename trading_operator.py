import asyncio
import datetime
import pprint
import time

import account
import data_getter
import strategy


class Operator:
    def __init__(self, client_info, sma_period, env_weight, rrr_rate, symbol='XRPUSDT'):
        self.account = account.Account(client_info=client_info, sma_period=sma_period, symbol=symbol)
        self.dataGetter = data_getter.DataGetter(client_info=client_info, sma_period=sma_period, symbol=symbol)
        self.strategy = strategy.Strategy(sma_period=sma_period, env_weight=env_weight, rrr_rate=rrr_rate)

        self.coin_data = self.dataGetter.get_info_period()  # LIST
        self.next_position = 0  # POS_OUT
        self.start_time = None
        self.start_balance = None
        self.sma_period = sma_period

    def make_coin_data(self):
        now_data = self.dataGetter.get_info()
        print(now_data)
        if len(self.coin_data) < self.sma_period:
            self.coin_data.append(now_data)
        elif len(self.coin_data) == self.sma_period:
            del self.coin_data[0]
            self.coin_data.append(now_data)

    async def execute_trading(self):
        self.start_time = datetime.datetime.now()
        print(f'START TIME :: {self.start_time}')
        try:
            while True:
                self.account.trading_order()
                self.make_coin_data()
                self.next_position = self.strategy.envelope_strategy(coin_data=self.coin_data)
                await time.sleep(300)
        except Exception as e:
            print(f'ERROR {e}')

    async def cmd_input(self):
        while True:
            key = await asyncio.get_event_loop().run_in_executor(None, input, "cmd (press h or help)> ")
            # help command
            if key == "help" or key == "h":
                print("help cmd")
            # get_account_info -> from self.account
            elif key == "info" or key == "i":
                print("** ACCOUNT INFORMATION **")
                print(self.account.get_account_info())
            # get_position_info -> from self.account
            elif key == "pos" or key == "p":
                print("** POSITION INFORMATION **")
                print(self.account.get_position_info())
            # get_trading_info -> from self.account
            elif key == "trade" or key == "h":
                print("** TRADING INFORMATION **")
                print(self.account.get_trading_info())
            # get_profit_info -> from self.account
            elif key == "profit" or key == "pnl":
                print("** PROFIT INFORMATION **")
                print(self.account.get_profit_info())
            # get_time_info -> from trading_operator.py
            elif key == "time" or key == "t":
                print("** TIME INFORMATION **")
                print(f'** START TIME : {self.start_time} **')
                print(f'**  NOW  TIME : {datetime.datetime.now()} **')
            # get_coin_data
            elif key == "coin" or key == "c":
                print("** COIN INFORMATION **")
                pprint.pprint(self.coin_data)
            # get_price_info -> from self.dataGetter
            elif key == "price" or key == "1":
                print("** PRICE INFORMATION **")
                print(self.dataGetter.get_book_info())
            # quit cmd
            elif key == "quit" or key == "q":
                print("** SUCCESSFULLY TERMINATED. **")
                # log trading_info
                asyncio.get_event_loop().stop()

    async def run_together(self):
        task_auto_trade = asyncio.create_task(self.execute_trading())
        task_check_input = asyncio.create_task(self.cmd_input())

        await asyncio.gather(task_auto_trade, task_check_input)

    @staticmethod
    def display_help_cmd():
        print("############# help cmd #############")
        print("# display account info \t\t --press info or i")
        print("# display trading info\t\t --press trade or h")
        print("# display profit info\t\t --press profit or pnl")
        print("# display time info\t\t --press time or t")
        print("# display coin data info\t --press coin or c")
        print("# display now price info\t -- press price or 1")
        print("# quit command \t\t\t --press quit or q")
