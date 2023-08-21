# -*- coding: utf-8 -*-
"""Assignment 3.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/18_gCwTgdg9QwbhONZIB2E_Q_UKm0RUW4
"""

import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM
from tensorflow.keras.layers import Dense, Dropout
import pandas as pd
from matplotlib import pyplot as plt
from sklearn.preprocessing import StandardScaler
import seaborn as sns
import yfinance as yf

start_date = '2019-03-01'
end_date = '2023-06-01'
df = yf.download('AAPL', start=start_date, end=end_date)
og_data = df

#Average Directonal Index(ADX)

n = 14
df['TR'] = np.maximum(np.maximum(df['High'] - df['Low'], abs(df['High'] - df['Close'].shift())), abs(df['Low'] - df['Close'].shift()))
df['DMplus'] = np.where((df['High'] - df['High'].shift()) > (df['Low'].shift() - df['Low']), np.maximum(df['High'] - df['High'].shift(), 0), 0)
df['DMminus'] = np.where((df['Low'].shift() - df['Low']) > (df['High'] - df['High'].shift()), np.maximum(df['Low'].shift() - df['Low'], 0), 0)
ATR = df['TR'].rolling(n).mean()
DMplus = df['DMplus'].rolling(n).mean()
DMminus = df['DMminus'].rolling(n).mean()
DIplus = DMplus / ATR * 100
DIminus = DMminus / ATR * 100
df['DIplus'] = DIplus
df['DIminus'] = DIminus
DX = abs(DIplus - DIminus) / (DIplus + DIminus) * 100
adx = DX.rolling(n).mean()

df = df.assign(ADX = adx)

df = df.drop(['TR','DMplus','DMminus','Adj Close','DIplus','DIminus'],axis=1)

df = df.rename(columns={'Close':'price'})

print(df)

##MACD

data = og_data
data['26_ema'] = data['Close'].ewm(span=26).mean()
data['12_ema'] = data['Close'].ewm(span=12).mean()
data['MACD'] = data['12_ema'] - data['26_ema']
data['signal_line'] = data['MACD'].ewm(span=9).mean()

print(data[['MACD', 'signal_line']])

MACD = data.loc[:,'MACD']
df.insert(3,'MACD',MACD,True)
print(df)

#Average True Range (ATR)

data['High-Low'] = data['High'] - data['Low']
data['High-PrevClose'] = abs(data['High'] - data['Close'].shift(1))
data['Low-PrevClose'] = abs(data['Low'] - data['Close'].shift(1))
data['TR'] = data[['High-Low', 'High-PrevClose', 'Low-PrevClose']].max(axis=1)

period = 14
data['ATR'] = data['TR'].rolling(period).mean()
mm = data['ATR']

print(data[['ATR']])

df.insert(4,'ATR',mm,True)
print(df)

#Accumulation and Distribution Indicator (ADL)

data['MF Multiplier'] = ((data['Close'] - data['Low']) - (data['High'] - data['Close'])) / (data['High'] - data['Low'])
data['MF Volume'] = data['MF Multiplier'] * data['Volume']
data['ADL'] = data['MF Volume'].cumsum()

nn = data['ADL']

print(data[['ADL']])

df.insert(5,'ADL',nn,True)
print(df)

new_cols = ['Volume','Open','High','Low','ADX','MACD','ATR','ADL','price']
df = df[new_cols]
df = df.iloc[64:]
df.to_csv("indicators.csv")
print(df)

df = pd.read_csv('indicators.csv')
print(df)
df=df.head(757)

cols = list(df)[1:10]
print(cols)

df_for_training = df[cols].astype(float)

scaler = StandardScaler()
scaler = scaler.fit(df_for_training)
df_for_training_scaled = scaler.transform(df_for_training)

trainX = []
trainY = []

n_future = 1   # Number of days we want to look into the future based on the past days.
n_past = 14    # Number of past days we want to use to predict the future.

for i in range(n_past, len(df_for_training_scaled) - n_future +1):
    trainX.append(df_for_training_scaled[i - n_past:i, 0:df_for_training.shape[1]])
    trainY.append(df_for_training_scaled[i + n_future - 1:i + n_future, 8])

trainX, trainY = np.array(trainX), np.array(trainY)

print('trainX shape == {}.'.format(trainX.shape))
print('trainY shape == {}.'.format(trainY.shape))

df_for_training_scaled

trainY

model = Sequential()
model.add(LSTM(64, activation='relu', input_shape=(trainX.shape[1], trainX.shape[2]), return_sequences=True))
model.add(LSTM(32, activation='relu', return_sequences=False))
model.add(Dropout(0.2))
model.add(Dense(trainY.shape[1]))

model.compile(optimizer='adam', loss='mse')
model.summary()

history = model.fit(trainX, trainY, epochs=5, batch_size=3, validation_split=0.1, verbose=1)

plt.plot(history.history['loss'], label='Training loss')
plt.plot(history.history['val_loss'], label='Validation loss')
plt.legend()

from pandas.tseries.holiday import USFederalHolidayCalendar
from pandas.tseries.offsets import CustomBusinessDay
us_bd = CustomBusinessDay(calendar=USFederalHolidayCalendar())

df2= df.head(1006)
train_dates = pd.to_datetime(df2['Date'])
print(train_dates.tail(15))
print(train_dates.shape[0])

n_past = 1
n_days_for_prediction=366

predict_period_dates = pd.date_range(list(train_dates)[-n_past], periods=n_days_for_prediction, freq='D').tolist()
print(predict_period_dates)

prediction = model.predict(trainX[-n_days_for_prediction:])

prediction_copies = np.repeat(prediction, df_for_training.shape[1], axis=-1)
y_pred_future = scaler.inverse_transform(prediction_copies)[:,8]

forecast_dates = []
for time_i in predict_period_dates:
    forecast_dates.append(time_i.date())

df_forecast = pd.DataFrame({'Date':np.array(forecast_dates), 'price':y_pred_future})
df_forecast['Date']=pd.to_datetime(df_forecast['Date'])

original = df[['Date', 'price']]
original['Date']=pd.to_datetime(original['Date'])
original

df_forecast

original.plot(x='Date',y='price')
original= pd.concat([original,df_forecast],axis=0)
original.plot(x='Date',y='price')

predicted = df_forecast
temp_df = pd.read_csv('indicators.csv')['Date'].values[756:1008]
print(len(predicted)-len(temp_df))
for i in predicted.index:
  tmp = str(predicted['Date'][i]).replace('T00:00:00.000000000','').replace(' 00:00:00', '')
  if tmp not in temp_df:
    predicted.drop(df.index[i:i+1], inplace=True)
print(len(predicted)-len(temp_df))
predicted.to_csv("predict.csv")

OGates = pd.read_csv('indicators.csv')['Date']
west = predicted.iloc[:,0]
print(OGates)

predicted_values = predicted.loc[:,"price"]

predicted_values = predicted_values.tolist()

print(predicted_values)

a = pd.read_csv('indicators.csv')
east = a.iloc[:,0]

actual = a.loc[:,"price"].values[756:1008]
actual_values = actual.tolist()
print(actual_values)
print(len(actual_values))

l=len(actual_values)
efficiency=[]
for i in range(0,l):
  e=100-((abs(actual_values[i]-predicted_values[i]))/actual_values[i])*100
  efficiency.append(e)
print(efficiency)

avg = np.average(efficiency)
print(avg)
