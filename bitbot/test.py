"""
position changed

testcase:
1. OUT -> LONG
2. OUT -> SHORT
3. LONG -> OUT
4. SHORT -> OUT
5. terminate_position (LONG/SHORT -> OUT)
"""
import trading_operator
from binance.client import Client

client = Client(api_key="", api_secret="")
dummyOperator = trading_operator.Operator(client_info=client, sma_period=10, env_weight=1, rrr_rate=1)

