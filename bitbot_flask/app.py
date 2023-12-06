import json
import time

from flask import Flask, render_template

app = Flask(__name__)

base_path = "../bitbot-live/BITBOT-LIVE/json_zip/"
overall_info_file_path = base_path+"overall_info.json"
statistics_file_path = base_path+"stat_info.json"
trading_info_file_path = base_path+"trading_info.json"
coin_data_file_path = base_path+"coin_data.json"


def update_all_json():
    with open(overall_info_file_path, 'r') as ova:
        overall_info = json.load(ova)
    with open(statistics_file_path, 'r') as stat:
        stat_info = json.load(stat)
    with open(coin_data_file_path, 'r') as coin:
        coin_data = json.load(coin)
    with open(trading_info_file_path, 'r') as trade:
        trading_info = json.load(trade)
    last_update_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

    return overall_info, stat_info, coin_data, trading_info, last_update_time


@app.route('/')
def index():
    data, stat, coin_data, trading_info, last_update_time = update_all_json()
    return render_template('trading_info.html',
                           data=data,
                           stat=stat,
                           coin_data=coin_data,
                           trading_info=trading_info,
                           last_update_time=last_update_time)


if __name__ == '__main__':
    app.run()
