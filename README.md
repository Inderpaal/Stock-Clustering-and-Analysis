# Stock Clustering and Analysis  

This project applies clustering techniques and time series analysis to stock market data. It groups stocks based on performance metrics and analyzes Tesla's stock price trends and its relationship with the S&P 500 index.  

---

## Table of Contents  
1. [Exploratory Data Analysis (EDA)](#exploratory-data-analysis-eda)  
2. [Clustering](#clustering)  
3. [Time Series Analysis](#time-series-analysis)  
4. [Results](#results)  
5. [Visualization](#visualization)  
6. [License](#license)  

---

## Exploratory Data Analysis (EDA)  
- Checked for missing values and cleaned the data.  
- Computed returns and volatility for clustering analysis.  
- Visualized correlations between stocks using a heatmap.  

---

## Clustering  
- Normalized data using `StandardScaler`.  
- Performed clustering using the following algorithms:  
  - K-Means  
  - Hierarchical Clustering  
  - Affinity Propagation  
- Evaluated clustering performance using elbow and silhouette scores.  

---

## Time Series Analysis  
- Decomposed Tesla's stock price into trend, seasonality, and residual components.  
- Analyzed lag relationships between Tesla's stock price and the S&P 500 index.  

---

## Results  

### Clustering  
- Stocks were grouped into clusters based on mean returns and volatility.  
- Visualization included clusters with centroids and key metrics.  

### Time Series Analysis  
- Tesla's stock prices were decomposed to reveal underlying trends and seasonality.  
- Lag analysis indicated the relationship between Tesla and S&P 500 performance.  

---

## Visualization  

- **Correlation Matrix**: Heatmap showing correlations between stocks.  
- **Clustering Scatter Plot**: Graph displaying clustered stocks and centroids.  
- **Time Series Decomposition**: Charts highlighting Tesla's trends, seasonality, and residuals.  

---

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

