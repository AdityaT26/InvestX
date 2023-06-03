import pandas as pd
import numpy as np
import tools
SYMBOL = "AAPL"

def calculate_rs(data, period):
    difference = np.diff(data)
    up = difference.clip(min=0)
    down = -difference.clip(max=0)
    avg_gain = tools.calculate_ema(up, period)
    avg_loss = tools.calculate_ema(down, period)
    rs = avg_gain/avg_loss
    return rs

def calculate_rsi(data, period):
    rs = calculate_rs(data, period)
    rsi = 100.0-(100.0/(1.0+rs))
    return rsi

def calculate_volrsi(volume, period=14):
    vrsi = calculate_rsi(volume, period)
    return vrsi

start_date = '2021-05-23'
end_date = '2023-05-23'

df = tools.getStockData(SYMBOL, start_date, end_date)
volume = df['Volume'].values

print(df.shape[0])

vrsi = calculate_volrsi(volume, period = 14)
extra_row = np.array([0])
vrsi = np.concatenate((vrsi, extra_row))

df['volume_rsi'] = vrsi

df.to_csv('volumersi_'+SYMBOL+'.csv', index=False)