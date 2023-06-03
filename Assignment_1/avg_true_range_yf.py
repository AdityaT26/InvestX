import tools
import numpy as np
import pandas as pd
SYMBOL = "AAPL"

def calculate_average_true_range(high, low, close, period=14):
    tr = calculate_true_range(high, low, close)
    atr = tools.calculate_ema(tr, period)
    return atr

def calculate_true_range(high, low, close):
    tr1 = high - low
    tr2 = np.abs(high - close[0:])
    tr3 = np.abs(low - close[0:])
    tr = np.maximum(tr1[0:], tr2, tr3)
    return tr


start_date = '2021-05-23'
end_date = '2023-05-23'

df = tools.getStockData(SYMBOL, start_date, end_date)
high = df['High'].values
low = df['Low'].values
close = df['Close'].values

atr = calculate_average_true_range(high, low, close)
df['atr'] = atr

df.to_csv('avgtruerange_'+SYMBOL+'.csv', index=False)