import newNonlive
import numpy as np
import pandas as pd

from hyperopt import fmin, tpe, hp

def objective(params):
    data = pd.read_csv('./xrp_df_5m_1y')
    risk_reward_ratio = params['risk_reward_ratio']
    envelope_period = int(params['envelope_period'])
    std_multiplier = params['std_multiplier']

    profit, _, win_rate = newNonlive.calculate_profit(data, risk_reward_ratio, envelope_period, std_multiplier)
    if win_rate < 30:  # If win_rate is less than 50%, set a high cost
        return 1e9
    else:
        return -profit

space = {
    'risk_reward_ratio': hp.uniform('risk_reward_ratio', 1.1, 5),
    'envelope_period': hp.quniform('envelope_period', 2, 40, 1),
    'std_multiplier': hp.uniform('std_multiplier', 0.1, 3)
}

best = fmin(fn=objective, space=space, algo=tpe.suggest, max_evals=200)
print(f'Best parameters: {best}')
data = pd.read_csv('./xrp_df_5m_1y')
# 최적의 파라미터를 사용하여 최종 수익률 계산
best_profit, best_total_trades, best_win_rate = newNonlive.calculate_profit(data, best['risk_reward_ratio'], int(best['envelope_period']), best['std_multiplier'])
print(f'Profit with best parameters: {best_profit}%')
print(f'Total trades with best parameters: {best_total_trades}')
print(f'Win rate with best parameters: {best_win_rate}%')
