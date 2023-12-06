import pandas as pd
import numpy as np
from hyperopt import fmin, tpe, hp

def calculate_profit(data, risk_reward_ratio, envelope_period, std_multiplier):
    # 인벨로프 밴드 계산
    data['sma'] = data['close'].rolling(window=envelope_period).mean()
    data['std'] = data['close'].rolling(window=envelope_period).std()
    data['upper'] = data['sma'] + (data['std'] * std_multiplier)
    data['lower'] = data['sma'] - (data['std'] * std_multiplier)

    data['cross_upper'] = (data['high'] > data['upper']).astype(int)
    data['cross_lower'] = (data['low'] < data['lower']).astype(int)

    position = 0  # 0: no position, 1: long, -1: short
    entry_price = 0
    exit_price = 0
    profit = 0
    total_trades = 0
    winning_trades = 0
    trading_fee = 0.07  # Trading fee per trade

    last_position = 0  # 마지막 포지션
    consecutive_losses = 0  # 연속 손실 횟수


    for i in range(len(data)):
        if position == 0:
            if data['cross_upper'].iloc[i] == 1 and not (last_position == -1 and consecutive_losses >= 2):  # Enter short position
                position = -1
                entry_price = data['close'].iloc[i]
                exit_price = entry_price + (entry_price - data['sma'].iloc[i]) * risk_reward_ratio
                total_trades += 1
                last_position = -1
                if consecutive_losses > 0:
                    consecutive_losses = 0
            elif data['cross_lower'].iloc[i] == 1 and not (last_position == 1 and consecutive_losses >= 2):  # Enter long position
                position = 1
                entry_price = data['close'].iloc[i]
                exit_price = entry_price - (data['sma'].iloc[i] - entry_price) * risk_reward_ratio
                total_trades += 1
                last_position = 1
                if consecutive_losses > 0:
                    consecutive_losses = 0
        elif position == -1:  # In a short position
            if data['low'].iloc[i] <= exit_price:  # Stop loss
                profit += ((entry_price - exit_price) / entry_price * 100) - trading_fee
                position = 0
                winning_trades += 1
                consecutive_losses += 1
            elif data['high'].iloc[i] >= data['sma'].iloc[i]:  # Take profit
                profit += ((entry_price - data['close'].iloc[i]) / entry_price * 100) - trading_fee
                position = 0
                if consecutive_losses > 0:
                    consecutive_losses = 0
        elif position == 1:  # In a long position
            if data['high'].iloc[i] >= exit_price:  # Stop loss
                profit -= ((exit_price - entry_price) / entry_price * 100) + trading_fee
                position = 0
                consecutive_losses += 1
            elif data['low'].iloc[i] <= data['sma'].iloc[i]:  # Take profit
                profit -= ((entry_price - data['close'].iloc[i]) / entry_price * 100) + trading_fee
                position = 0
                winning_trades += 1
                if consecutive_losses > 0:
                    consecutive_losses = 0



    if total_trades > 0:
        win_rate = (winning_trades / total_trades) * 100
    else:
        win_rate = 0

    return profit, total_trades, win_rate

def objective(params):
    data = pd.read_csv('./xrp_df_5m_1y')
    risk_reward_ratio = params['risk_reward_ratio']
    envelope_period = int(params['envelope_period'])
    std_multiplier = params['std_multiplier']

    profit, _, win_rate = calculate_profit(data, risk_reward_ratio, envelope_period, std_multiplier)
    if win_rate < 50:  # If win_rate is less than 50%, set a high cost
        return 1e9
    else:
        return -profit

space = {
    'risk_reward_ratio': hp.uniform('risk_reward_ratio', 1.1, 10),
    'envelope_period': hp.quniform('envelope_period', 2, 200, 1),
    'std_multiplier': hp.uniform('std_multiplier', 0.1, 10)
}

# best = fmin(fn=objective, space=space, algo=tpe.suggest, max_evals=200)
# print(f'Best parameters: {best}')
data = pd.read_csv('./xrp_df_5m_2w')
# 최적의 파라미터를 사용하여 최종 수익률 계산
# best_profit, best_total_trades, best_win_rate = calculate_profit(data, best['risk_reward_ratio'], int(best['envelope_period']), best['std_multiplier'])
# print(f'Profit with best parameters: {best_profit}%')
# print(f'Total trades with best parameters: {best_total_trades}')
# print(f'Win rate with best parameters: {best_win_rate}%')
# #
profit, total_trades, win_rate = calculate_profit(data, 4.82889, 21, 2.58904)
print(f'Profit: {profit}%')
print(f'Total trades: {total_trades}')
print(f'Win rate: {win_rate}%')
