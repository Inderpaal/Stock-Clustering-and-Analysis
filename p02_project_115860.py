# -*- coding: utf-8 -*-
"""P02-Project-115860.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1G5oy02-4l90cAErQomD0-CH3d9Aq-jA9

**FINC612**

**Big Data and Machine Learning Tools & Techniques**

**FINAL PROJECT Semester 2, 2024**

**INDERPAAL SINGH RATHNA BALAJI - 1158660**

________________________________________________________________________________

Question:

To recommend on adding a given asset (“NVDA”) to an existing portfolio

Methods of assessment:
1.	Checking if the asset is different from the existing assets of the portfolio using clustering algorithms:

    a. K-Means clustering

    b. Affinity Propagation
      

2.	Checking the sentiment of the news and articles of asset using NLP and sentiment analysis.

3.	Checking the future value of the asset (next 30 days) using:

    a.	SARIMAX (TIME SERIES ANALYSIS)

    b. LSTM

______________________________________________________________________________

By doing these, we can get to know if

1. The asset is a good addition to the portfolio based on volatility

2. The sentiment of the internet of the asset

3. Checking the future of the asset value(30 days)

#Importing librares and packages
"""

!pip install yfinance
!pip install sentencepiece
!pip install transformers

import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pandas import read_csv, set_option
from pandas.plotting import scatter_matrix
import seaborn as sns
from sklearn.preprocessing import StandardScaler
import datetime

#Import Model Packages
from sklearn.cluster import KMeans, AgglomerativeClustering, AffinityPropagation
from scipy.cluster.hierarchy import fcluster
from scipy.cluster.hierarchy import dendrogram, linkage, cophenet
from scipy.spatial.distance import pdist
from sklearn.metrics import adjusted_mutual_info_score
from sklearn import cluster, covariance, manifold
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score


#Other Helper Packages and functions
import matplotlib.ticker as ticker
from itertools import cycle

#For NLP
from transformers import PegasusForConditionalGeneration, AutoTokenizer
from bs4 import BeautifulSoup
import requests

#For LSTM
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.optimizers import Adam

"""#Checking if the NVDA is a good fit to the exsisting portfolio using *Clustering algorithms*

## Data Collection and preparation

'PEAK' - is delisted. So removed from the list
"""

tickers = ['BDX', 'BK', 'BLK', 'BRO', 'C', 'CB', 'CDW', 'CINF', 'CMCSA', 'CME', 'CMG', 'CPT',
'MCD', 'MCHP', 'MGM', 'MMC', 'MO', 'MSI', 'MTD', 'NEM', 'NI', 'NVR', 'ORCL',
'ORLY', 'PEP', 'PFE', 'PGR', 'PNW', 'RF', 'RHI', 'RL', 'SJM', 'SPG', 'STLD',
'STX', 'TECH', 'TEL', 'TER', 'TMUS', 'TRGP',  'UDR', 'UNP', 'VTR', 'WEC', 'WHR',
'WTW', 'XRAY', 'XYL', 'GOOG', 'HBAN', 'HES', 'HII', 'HPQ','NVDA']

ohlc = yf.download(tickers, start = '2021-10-15', end = '2024-10-15')
prices = ohlc["Adj Close"].dropna(how="all")
prices.tail()

prices.describe()

"""##Finding the correlation between the stocks and how the movement of each stock affets the other"""

# correlation
correlation = prices.corr()
plt.figure(figsize=(25,25))
plt.title('Correlation Matrix')
sns.heatmap(correlation, vmax=1, square=True,annot=True,cmap='cubehelix')

#Checking for any null values and removing the null values'''
print('Null Values =', prices.isnull().values.any())

"""##Data Preparation for clustering model"""

#Calculate average annual percentage return and volatilities over a theoretical one year period
returns = prices.pct_change().mean() * 252
returns = pd.DataFrame(returns)
returns.columns = ['Returns']
returns['Volatility'] = prices.pct_change().std() * np.sqrt(252)
data=returns

"""scaling"""

from sklearn.preprocessing import StandardScaler
scaler = StandardScaler().fit(data)
rescaledDataset = pd.DataFrame(scaler.fit_transform(data),columns = data.columns, index = data.index)
# summarize transformed data
rescaledDataset.head(2)
X=rescaledDataset
X.head(5)

"""## K-Means Clustering

"""

nclust=7

#Fit with k-means
k_means = cluster.KMeans(n_clusters=nclust)
k_means.fit(X)

#We extract the important parameters from the k-means clustering
centroids, assignments, inertia = k_means.cluster_centers_, k_means.labels_, k_means.inertia_

#Extracting labels
target_labels = k_means.predict(X)
#Printing the labels
target_labels

"""<a id='5.1.1'></a>
### 5.1.1. Finding optimal number of clusters

Find the flat line and the lower value is the optimal number of clusters
"""

distorsions = []
max_loop=20
for k in range(2, max_loop):
    kmeans_test = KMeans(n_clusters=k)
    kmeans_test.fit(X)
    distorsions.append(kmeans_test.inertia_)
fig = plt.figure(figsize=(15, 5))
plt.plot(range(2, max_loop), distorsions)
plt.xticks([i for i in range(2, max_loop)], rotation=75)
plt.grid(True)

"""#### Silhouette score

According to to the silhouette score, the lowerest point of the first decline is 7. So we take the number of clusters to be 7
"""

from sklearn import metrics

silhouette_score = []
for k in range(2, max_loop):
        kmeans_test = KMeans(n_clusters=k,  random_state=10, n_init=10)
        kmeans_test.fit(X)
        silhouette_score.append(metrics.silhouette_score(X, kmeans_test.labels_, random_state=10))
fig = plt.figure(figsize=(15, 5))
plt.plot(range(2, max_loop), silhouette_score)
plt.xticks([i for i in range(2, max_loop)], rotation=75)
plt.grid(True)

"""<a id='5.1.2'></a>
### 5.1.2. Cluster Visualisation
"""

centroids = k_means.cluster_centers_
fig = plt.figure(figsize=(16,10))
ax = fig.add_subplot(111)
scatter = ax.scatter(X.iloc[:,0],X.iloc[:,1], c = k_means.labels_, cmap ="rainbow", label = X.index)
ax.set_title('k-Means')
ax.set_xlabel('Mean Return')
ax.set_ylabel('Volatility')
plt.colorbar(scatter)

# zip joins x and y coordinates in pairs
for x,y,name in zip(X.iloc[:,0],X.iloc[:,1],X.index):

    label = name

    plt.annotate(label, # this is the text
                 (x,y), # this is the point to label
                 textcoords="offset points", # how to position the text
                 xytext=(0,10), # distance from text to points (x,y)
                 ha='center') # horizontal alignment can be left, right or center

plt.plot(centroids[:,0],centroids[:,1],'sg',markersize=11)

# @title
cluster_label = pd.concat([pd.DataFrame(X.index), pd.DataFrame(k_means.labels_)],axis = 1)
cluster_label.columns =['Company','Cluster']
cluster_label.sort_values(by=['Cluster'])

"""## Affinity Propagation

"""

ap = AffinityPropagation(damping = 0.5, max_iter = 250, affinity = 'euclidean')
ap.fit(X)
clust_labels2 = ap.predict(X)

fig = plt.figure(figsize=(16,10))
ax = fig.add_subplot(111)
scatter = ax.scatter(X.iloc[:,0],X.iloc[:,1], c =clust_labels2, cmap ="rainbow")
ax.set_title('Affinity')
ax.set_xlabel('Mean Return')
ax.set_ylabel('Volatility')
plt.colorbar(scatter)

# zip joins x and y coordinates in pairs
for x,y,name in zip(X.iloc[:,0],X.iloc[:,1],X.index):

    label = name

    plt.annotate(label, # this is the text
                 (x,y), # this is the point to label
                 textcoords="offset points", # how to position the text
                 xytext=(0,10), # distance from text to points (x,y)
                 ha='center') # horizontal alignment can be left, right or center

cluster_centers_indices = ap.cluster_centers_indices_
labels = ap.labels_
n_clusters_ = len(cluster_centers_indices)

cluster_centers_indices = ap.cluster_centers_indices_
labels = ap.labels_
no_clusters = len(cluster_centers_indices)

print('Estimated number of clusters: %d' % no_clusters)
# Plot exemplars

X_temp=np.asarray(X)
plt.close('all')
plt.figure(1)
plt.clf()

fig = plt.figure(figsize=(8,6))
colors = cycle('bgrcmykbgrcmykbgrcmykbgrcmyk')
for k, col in zip(range(n_clusters_), colors):
    class_members = labels == k
    cluster_center = X_temp[cluster_centers_indices[k]]
    plt.plot(X_temp[class_members, 0], X_temp[class_members, 1], col + '.')
    plt.plot(cluster_center[0], cluster_center[1], 'o', markerfacecolor=col, markeredgecolor='k', markersize=14)
    for x in X_temp[class_members]:
        plt.plot([cluster_center[0], x[0]], [cluster_center[1], x[1]], col)

plt.show()

cluster_label = pd.concat([pd.DataFrame(X.index), pd.DataFrame(ap.labels_)],axis = 1)
cluster_label.columns =['Company','Cluster']
cluster_label.sort_values(by=['Cluster'])

"""K Means clustering:

*   The total number of clusters is 7. And thus number of stocks in the same cluster as the stock is 0.
*   Visually, The stock of NVDA is seperated from the rest of the stocks.

Affinity Propogation:

*   The total number of clusters is 8. And thus number of stocks in the same cluster as the stock is 0.
*   Visually, The stock of NVDA is seperated from the rest of the stocks.

SO as you can see, the algorithms are indicating that 'NVDA' is quite different from the exsisting stocks in the portfolio.

_______________________________________________________________________________

# Analysing the news around the web.
"""

model_name = "human-centered-summarization/financial-summarization-pegasus"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = PegasusForConditionalGeneration.from_pretrained(model_name)

monitored_tickers = ['NVDA']

def search_for_stock_news_urls(ticker):
    search_url = "https://www.google.com/search?q=yahoo+finance+{}&tbm=nws".format(ticker)
    r = requests.get(search_url)
    soup = BeautifulSoup(r.text, 'html.parser')
    atags = soup.find_all('a')
    hrefs = [link['href'] for link in atags]
    return hrefs

raw_urls = {ticker:search_for_stock_news_urls(ticker) for ticker in monitored_tickers}
raw_urls

raw_urls['NVDA']

import re

exclude_list = ['maps', 'policies', 'preferences', 'accounts', 'support']

def strip_unwanted_urls(urls, exclude_list):
    val = []
    for url in urls:
        if 'https://' in url and not any(exclude_word in url for exclude_word in exclude_list):
            res = re.findall(r'(https?://\S+)', url)[0].split('&')[0]
            val.append(res)
    return list(set(val))

cleaned_urls = {ticker:strip_unwanted_urls(raw_urls[ticker], exclude_list) for ticker in monitored_tickers}
cleaned_urls

def scrape_and_process(URLs):
    ARTICLES = []
    for url in URLs:
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        paragraphs = soup.find_all('p')
        text = [paragraph.text for paragraph in paragraphs]
        words = ' '.join(text).split(' ')[:350]
        ARTICLE = ' '.join(words)
        ARTICLES.append(ARTICLE)
    return ARTICLES

articles = {ticker:scrape_and_process(cleaned_urls[ticker]) for ticker in monitored_tickers}
articles

def summarize(articles):
    summaries = []
    for article in articles:
        input_ids = tokenizer.encode(article, return_tensors='pt', max_length=55, truncation=True)
        output = model.generate(input_ids, max_length=55, num_beams=5, early_stopping=True)
        summary = tokenizer.decode(output[0], skip_special_tokens=True)
        summaries.append(summary)
    return summaries

summaries = {ticker:summarize(articles[ticker]) for ticker in monitored_tickers}
summaries

from transformers import pipeline
sentiment = pipeline('sentiment-analysis')

sentiment(summaries['NVDA'])

scores = {ticker:sentiment(summaries[ticker]) for ticker in monitored_tickers}
scores

"""As you can see, The scores of of the textual analysis indicate that the sentiments of the articles regarding 'NVDA' on yahoo finance is mostly positive. Meaning that the market sentiment is POSITIVE.

________________________________________________________________________________

#Forecasting to see the furure values using SARIMAX and LSTM
"""

tikers = ["NVDA"]

fc = yf.download(tikers, start="2020-01-01", end ="2024-01-01")

fc.head(5)

# Get adj close
fc = fc['Adj Close']

fc.head(5)

data_length = len(fc)
data_length

from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

# Augmented Dickey-Fuller test
result = adfuller(fc)
print('ADF Statistic:', result[0])
print('p-value:', result[1])
print('Critical Values:', result[4])

"""### We get P>0.05 hence our data is not stationary, so we will use differencing to make the data stationary.

In the below code we Use first order differencing to check whether the data is stationary or not.
"""

result = adfuller(fc)
print('ADF Statistic:', result[0])
print('p-value:', result[1])
print('Critical Values:', result[4])


if result[1] > 0.05:  # If p-value is greater than 0.05, the series is likely non-stationary
    # Apply differencing (you might need to experiment with the order)
    fc_diff = fc.diff().dropna()  # First-order differencing

    # Perform ADF test on the differenced series
    result_diff = adfuller(fc_diff)
    print('Differenced ADF Statistic:', result_diff[0])
    print('Differenced p-value:', result_diff[1])

    # If still not stationary, you can try higher-order differencing
    # fc_diff = fc.diff().diff().dropna()  # Second-order differencing

else:
    print("The original time series is already stationary.")

"""After applying the Differencing we get a P Value which is Smaller than 0.05 hence now our data is Stationary."""

# Plot ACF and PACF
fig, axes = plt.subplots(1, 2, figsize=(15, 5))

plot_acf(fc, ax=axes[0])
plot_pacf(fc, ax=axes[1])

plt.show()

"""This shows that the lag is 8.

###Seasonality

This shows that the lag is 8.
"""

decomposition = seasonal_decompose(fc, model='additive', period=12)

# Plot the decomposed components
plt.figure(figsize=(12, 8))

plt.subplot(411)
plt.plot(decomposition.observed, label='Observed')
plt.legend(loc='best')

plt.subplot(412)
plt.plot(decomposition.trend, label='Trend')
plt.legend(loc='best')

plt.subplot(413)
plt.plot(decomposition.seasonal, label='Seasonal')
plt.legend(loc='best')

plt.subplot(414)
plt.plot(decomposition.resid, label='Residual')
plt.legend(loc='best')

plt.tight_layout()
plt.show()

"""Using SARIMAX"""

from statsmodels.tsa.statespace.sarimax import SARIMAX


# Download data from Yahoo Finance
df = yf.download(["NVDA","^GSPC"], start = '2021-10-15', end = '2024-10-15')
# Extract adj closing prices
df = df['Adj Close']
df['sp500_Lag_1'] = df['^GSPC'].shift(1)
df['sp500_Lag_2'] = df['^GSPC'].shift(2)
df['sp500_Lag_3'] = df['^GSPC'].shift(3)

df = df[["sp500_Lag_1","sp500_Lag_2","sp500_Lag_3","NVDA","^GSPC"]]
df = df.dropna()


# Check for missing and infinite values
print(df.isnull().sum())
print(np.isinf(df).sum())

# Fill missing values with 0
df.fillna(0, inplace=True)

# Create the SARIMAX model
model = SARIMAX(endog=df['NVDA'], exog=df[['sp500_Lag_1','sp500_Lag_2','sp500_Lag_3']], order=(8, 1, 7), seasonal_order=(1, 1, 1, 12))
model_fit = model.fit()

# Print the model summary
print(model_fit.summary())

# Get predictions
predictions = model_fit.get_prediction()
predicted_mean = predictions.predicted_mean

# Evaluate the model
mse = mean_squared_error(df['NVDA'], predicted_mean)
rmse = mean_squared_error(df['NVDA'], predicted_mean, squared=False)
mae = mean_absolute_error(df['NVDA'], predicted_mean)
r2 = r2_score(df['NVDA'], predicted_mean)

print(f"Mean Squared Error (MSE): {mse:.4f}")
print(f"Root Mean Squared Error (RMSE): {rmse:.4f}")
print(f"Mean Absolute Error (MAE): {mae:.4f}")
print(f"R-squared (R2): {r2:.4f}")

# Plot the actual and predicted values
plt.plot(df['NVDA'], label='Actual')
plt.plot(predicted_mean, label='Predicted')
plt.legend()
plt.title('NVDA Actual vs Predicted Values')
plt.show()

# Predict next 30 days with SP500 data as exogenous variable (lagged by 3)
last_exog_values = df[['sp500_Lag_1', 'sp500_Lag_2', 'sp500_Lag_3']].iloc[-1].values.reshape(1, -1)  # Get last values and reshape
forecast_exog = pd.DataFrame(np.repeat(last_exog_values, 30, axis=0), columns=['sp500_Lag_1', 'sp500_Lag_2', 'sp500_Lag_3'],
                             index=pd.date_range(start=df["NVDA"].index[-1] + pd.Timedelta(days=1), periods=30))


forecast = model_fit.get_forecast(steps=30, exog=forecast_exog)

forecast_values = forecast.predicted_mean
confidence_intervals = forecast.conf_int()

# Create a new dataframe to store the predictions
forecast_dates = pd.date_range(start=df["NVDA"].index[-1] + pd.Timedelta(days=1), periods=30)
forecast_df = pd.DataFrame({'Forecast': forecast_values}, index=forecast_dates)

# Plot historical NVDA prices along with forecasted values
plt.figure(figsize=(10,6))
plt.plot(df["NVDA"], label='NVDA Close Price History', color='blue')
plt.plot(forecast_df['Forecast'], label='NVDA Forecast', color='green')

# Adding confidence intervals
plt.fill_between(forecast_dates,
                 confidence_intervals.iloc[:, 0],
                 confidence_intervals.iloc[:, 1],
                 color='green', alpha=0.2)

plt.title('NVDA Stock Price Prediction with SARIMAX (Next 30 Days)')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend()
plt.show()

"""________________________________________________________________________________

LSTM
"""

df['NVDA_lag1'] = df['NVDA'].shift(1)
df['NVDA_lag2'] = df['NVDA'].shift(2)
df['NVDA_lag3'] = df['NVDA'].shift(3)

df = df[["NVDA_lag1","NVDA_lag2","NVDA_lag3","sp500_Lag_1","sp500_Lag_2","sp500_Lag_3","NVDA","^GSPC"]]
df = df.dropna()



# Define features (S&P 500 lags) and target (NVDA price)
X = df[["sp500_Lag_1","sp500_Lag_2","sp500_Lag_3"]]
y = df['NVDA']

# Scaling the df
scaler_X = MinMaxScaler()
scaler_y = MinMaxScaler()

X_scaled = scaler_X.fit_transform(X)
y_scaled = scaler_y.fit_transform(y.values.reshape(-1, 1))

# Reshaping for LSTM [samples, time steps, features]
X_scaled = X_scaled.reshape((X_scaled.shape[0], 1, X_scaled.shape[1]))

# Train-test split (80% training, 20% testing)
train_size = int(len(X_scaled) * 0.8)
X_train, X_test = X_scaled[:train_size], X_scaled[train_size:]
y_train, y_test = y_scaled[:train_size], y_scaled[train_size:]

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
model = Sequential()
model.add(LSTM(50, activation='relu', return_sequences=True, input_shape=(1, 3)))
model.add(Dropout(0.2))# to reduce overfitting
model.add(LSTM(25, activation='relu'))
model.add(Dropout(0.2))
model.add(Dense(1))

# Compile the model
#model.compile(optimizer=Adam(), loss='mse', metrics=['mae'])
model.compile(optimizer=Adam(learning_rate=0.001), loss='mse', metrics=['mae'])

# Train the model
history = model.fit(X_train, y_train, epochs=100, batch_size=32, validation_data=(X_test, y_test), verbose=0)

model.summary()

# prompt: evaluate the model with mae, mse, rmse, r squared
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np
# y_pred contains the model's predictions on the test set
y_pred = model.predict(X_test)

# Take the first prediction from y_pred to match the shape of y_test
y_pred = y_pred[:, 0] # Select only the first prediction for each sample
# Calculate MAE
mae = mean_absolute_error(y_test, y_pred)
# Calculate MSE
mse = mean_squared_error(y_test, y_pred)
# Calculate RMSE
rmse = np.sqrt(mse)
# Calculate R-squared
r2 = r2_score(y_test, y_pred)

print(f"Mean Absolute Error (MAE): {mae}")
print(f"Mean Squared Error (MSE): {mse}")
print(f"Root Mean Squared Error (RMSE): {rmse}")
print(f"R-squared (R2): {r2}")

# Plot learning curve
plt.plot(history.history['loss'], label='Train Loss')
plt.plot(history.history['val_loss'], label='Test Loss')
plt.legend()
plt.title('Model Learning Curve')
plt.show()

def predict_next_30_days(model, last_10_days_sp500, scaler_y):
    predictions = []
    # Use the last 10 days as the starting point for the predictions
    input_seq = last_10_days_sp500.reshape((1, 1, last_10_days_sp500.shape[0]))

    for _ in range(30):
        # Predict the next day
        predicted_price = model.predict(input_seq)

        # Reshape the prediction to its original scale
        predicted_price_rescaled = scaler_y.inverse_transform(predicted_price)
        predictions.append(predicted_price_rescaled[0, 0])

        # Prepare the input sequence for the next prediction
        input_seq = np.roll(input_seq, -1, axis=2)
        input_seq[0, 0, -1] = predicted_price  # Update with the latest prediction

    # Return predictions as an array for easy plotting
    return np.array(predictions)

# Get the last 10 days of the S&P 500 data from the test set
last_10_days_sp500_scaled = X_scaled[-1, 0, :]  # Last row of X_test, last 10 days

# Predict the next 30 days for the stock using the last S&P 500 values
predicted_30_days = predict_next_30_days(model, last_10_days_sp500_scaled, scaler_y)

# Plot the predicted trend
plt.figure(figsize=(10, 6))
plt.plot(np.arange(0, 30), predicted_30_days, label='Predicted AMZN Prices (Next 30 Days)', color='red')
plt.title('Predicted Trend of AMZN Stock Prices (Next 30 Days)')
plt.xlabel('Days')
plt.ylabel('Price')
plt.legend()
plt.show()

# Rescale y_test to original scale for comparison
y_test_rescaled = scaler_y.inverse_transform(y_test)

# Plot the actual prices (the last 100 days) and the predicted next 30 days
plt.figure(figsize=(12, 8))
plt.plot(np.arange(0, len(y_test_rescaled[-100:])), y_test_rescaled[-100:], label='Actual NVDA Prices', color='blue')
plt.plot(np.arange(len(y_test_rescaled[-100:]), len(y_test_rescaled[-100:]) + 30), predicted_30_days.flatten(), label='Predicted NVDA Prices (Next 30 Days)', color='red')
plt.title('NVDA Stock Prices: Actual vs Predicted (Next 30 Days)')
plt.xlabel('Days')
plt.ylabel('Price')
plt.legend()
plt.grid(True)
plt.show()

"""LSTM model is not being able to forecast even after changing layers, neurons. SO for forecasting the price of NVDA stock we use TIMESERIES analtsis using SARIMAX

________________________________________________________________________________
As it is evident fromthe clustering algorithms, sentiment analysis, forecasting algorithms,

It is **recommended** to add the stock to the portfolio for the following reasons:
1.	From Method (1), the stock will be a good addition to the portfolio as it will diversify the portfolio and thus make it more stable.
2.	From Method (2), the current and historical market sentiment for the stock has been mostly positive, meaning that the stock is being well received by the public and has a good opinion.
3.	From method (3), the future forecast of the stock is promising as it seems to be stable  and growing for the next 30days (1month).
"""