import pandas as pd
import NonLiveAdvanced as nlbt


def main(argv):
    xrp_df =pd.read_csv('./xrp_df_5m_1y')
    backtesting = nlbt.NonLiveBacktesting(xrp_df)
    for sma_period in range(1, 20):
        for env_weight in range(1, 5):
            backtesting.execute(env_weight=env_weight/100, sma_period=sma_period)


if __name__ == '__main__':
    import sys
    main(sys.argv)
