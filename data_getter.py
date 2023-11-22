from binance.enums import KLINE_INTERVAL_5MINUTE


class DataGetter:
    def __init__(self, client_info, sma_period, symbol='XRPUSDT'):
        self.client = client_info
        self.symbol = symbol
        self.sma_period = sma_period

    def get_info(self):
        data = self.client.futures_klines(
            symbol=self.symbol,
            interval=KLINE_INTERVAL_5MINUTE,
            limit=1
        )
        coin_data = {"time": data[0][0],
                     "open": float(data[0][1]),
                     "close": float(data[0][4]),
                     "volume": float(data[0][5])}
        return coin_data

    def get_info_period(self):
        candle_data = self.client.futures_klines(
            symbol=self.symbol,
            interval=KLINE_INTERVAL_5MINUTE,
            limit=self.sma_period + 1
        )
        coin_list = [{"time": data[0],
                      "open": float(data[1]),
                      "close": float(data[4]),
                      "volume": float(data[5])}
                     for data in candle_data]
        coin_list = coin_list[:-2]
        return coin_list

    def get_book_info(self):
        ticker_info = self.client.get_ticker(symbol=self.symbol)
        return {"bid_price": float(ticker_info['bidPrice']),
                "ask_price": float(ticker_info['askPrice'])}
