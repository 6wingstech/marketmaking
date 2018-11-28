from binance.client import Client
from binance.enums import *
import pandas as pd


bina = Client('KEY', 'SECRET')
#bina = ccxt.binance()

def load_dataframe(pair, timeframe):
    mkt_data = bina.get_historical_klines(pair, Client.KLINE_INTERVAL_5MINUTE, timeframe)
    df = pd.DataFrame(data=mkt_data, columns=[0, 'Open', 'High', 'Low', 'Close', 'Volume', 6, 'Base Volume', 8, 9, 10, 11]).astype(float)
    df = df.drop(columns = [0, 6, 8, 9, 10, 11])
    return df

def coin_quote(pair):
    depth = bina.get_order_book(symbol=pair)
    bid = float(depth['bids'][0][0])
    ask = float(depth['asks'][0][0])
    return bid, ask

def get_all_tickers():
	return bina.get_all_tickers()
