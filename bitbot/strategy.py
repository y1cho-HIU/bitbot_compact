"""
we have already strategy class.
input : (list)coin_data
output : (bool)signal, (POS)next_position
"""
import statistics


class Strategy:
    POS_OUT = 0
    POS_LONG = 1
    POS_SHORT = -1

    def __init__(self, sma_period, env_weight, rrr_rate):
        self.now_position = self.POS_OUT
        self.target_price = -1
        self.loss_price = -1
        self.sma_period = sma_period
        self.env_weight = env_weight
        self.rrr_rate = rrr_rate

    @staticmethod
    def get_sma(coin_data):
        """
        :param coin_data: [{time, open, close, volume}, ]
        :return: now_sma for strategy
        """
        close_list = [data['close'] for data in coin_data]
        return round(sum(close_list) / len(close_list), 6)

    @staticmethod
    def get_std_dev(coin_data):
        close_list = [data['close'] for data in coin_data]
        return round(statistics.stdev(close_list), 6)

    def set_now_position(self, position):
        self.now_position = position

    def set_target_price(self, position, now_sma, env_price):
        if position == self.POS_LONG:
            self.target_price = now_sma
            self.loss_price = env_price - (now_sma - env_price) / self.rrr_rate
        elif position == self.POS_SHORT:
            self.target_price = now_sma
            self.loss_price = env_price + (now_sma - env_price) / self.rrr_rate

    def set_target_price_out(self):
        self.target_price = -1
        self.loss_price = -1

    def envelope_strategy(self, coin_data):
        """ default signal, next_position -> not change """
        signal = False
        next_position = self.now_position

        now_sma = self.get_sma(coin_data)
        std_dev = self.get_std_dev(coin_data)
        now_price = coin_data[-1]['close']
        env_up = round(now_sma + (std_dev * self.env_weight), 6)
        env_down = round(now_sma - (std_dev * self.env_weight), 6)

        if self.now_position == self.POS_OUT:
            if now_price <= env_down:
                next_position = self.POS_LONG
                self.set_target_price(self.POS_LONG, now_sma, env_down)
            if now_price >= env_up:
                next_position = self.POS_SHORT
                self.set_target_price(self.POS_SHORT, now_sma, env_up)

        elif self.now_position == self.POS_LONG:
            if (now_price >= self.target_price) | (now_price <= self.loss_price):
                next_position = self.POS_OUT
                self.set_target_price_out()
        elif self.now_position == self.POS_SHORT:
            if (now_price <= self.target_price) | (now_price >= self.loss_price):
                next_position = self.POS_OUT
                self.set_target_price_out()

        """
        signal is True -> trading
        signal is False -> nothing
        """
        if self.now_position != next_position:
            signal = True
        return signal, next_position

    def get_target_price(self):
        return {"target_price": {self.target_price},
                "loss_price": {self.loss_price}}