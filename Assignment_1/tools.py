import numpy as np
import yfinance as yf
import pandas as pd

def calculate_ema(data, period):
    weights = np.exp(np.linspace(-1., 0., period))
    weights /= weights.sum()
    ema = np.convolve(data, weights, mode='full')[:len(data)]
    ema[:period-1] = ema[period-1]
    return ema
    
def getStockData(symbol, start_date, end_date):
    # Retrieve the stock data using yfinance
    stock_data = yf.download(symbol, start=start_date, end=end_date)

    # Create a DataFrame from the stock data
    df = pd.DataFrame(stock_data, columns=['Open', 'High', 'Low', 'Close', 'Volume'])
    df.reset_index(inplace=True)
    df.rename(columns={'Date': 'Date'}, inplace=True)
    df = df.dropna()
    return df

