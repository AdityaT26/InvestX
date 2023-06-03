import pandas as pd
import numpy as np
import tools

SYMBOL = "AAPL"

def calculate_macd(close_prices, fast_period=12, slow_period=26, signal_period=9):

    fast_ema = tools.calculate_ema(close_prices, fast_period)
    slow_ema = tools.calculate_ema(close_prices, slow_period)

    macd_line = fast_ema - slow_ema

    signal_line = tools.calculate_ema(macd_line, signal_period)

    return macd_line, signal_line

start_date = '2021-05-23'
end_date = '2023-05-23'

df = tools.getStockData(SYMBOL, start_date, end_date)

print(df)

close_prices = df['Close'].values
macd, signal = calculate_macd(close_prices)
df['MACD'] = np.append(np.nan, macd[:-1])
df['Signal'] = np.append(np.nan, signal[:-1])

df.to_csv('macd_'+SYMBOL+'.csv', columns=['Date', 'MACD', 'Signal'], index=False)

