import asyncio
import json
import sys

import requests
from binance.client import Client

import trading_operator

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("python main.py 0/1")

    mode = int(sys.argv[1])
    client = None
    with open('./json_repository/account.json', 'r') as api:
        api_data = json.load(api)

    if mode == 0:
        # client info = testnet mode
        print('testnet mode')
        test_api_key = api_data['test_api_key']
        test_api_secret = api_data['test_api_secret']
        client = Client(api_key=test_api_key, api_secret=test_api_secret, testnet=True)
    elif mode == 1:
        # client info = real-trading mode
        print('real-trading mode')
        api_key = api_data['api_key']
        api_secret = api_data['api_secret']
        client = Client(api_key=api_key, api_secret=api_secret)

    myOperator = trading_operator.Operator(client_info=client,
                                           sma_period=api_data['sma_period'],
                                           env_weight=api_data['env_weight'],
                                           rrr_rate=api_data['rrr_rate'],
                                           symbol=api_data['symbol'])

    if api_data['ip_info'] == requests.get('http://ip.jsontest.com').json()['ip']:
        try:
            async def run_together():
                task_auto_trade = asyncio.create_task(myOperator.execute_trading())
                task_check_cmd = asyncio.create_task(myOperator.cmd_input())
                await asyncio.gather(task_auto_trade, task_check_cmd)

            asyncio.run(run_together())
        except Exception as e:
            print(f'__main__ ERROR : {e}')
    else:
        print('PLEASE CHECK YOUR IP ADDRESS AGAIN.')
