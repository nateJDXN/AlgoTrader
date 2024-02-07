# AlgoTrader

This Jupyter notebook is a work in progress of a KNN machine learning model.

It uses a set of indicators including Volume, ATR, RSI, and moving averages taken from a variable number of past candles (~20). 

**The first model**
The original approach was to randomly sample candles from the price data to fit the model (80% for training and 20% for testing). The problem with this approach appeared when testing where there was no relation from candle to candle since they were randomly sampled.
The current apporach trains on the first 80% of price data, and tests on the remaining 20%, which better simulates real world data. 

*Update 1/29/24*
The model is currently overfitting, yielding a 94.1% accuracy which is unreasonably high.


**XGBoost**
The more powerful model 

### Requirements
- pandas
- numpy
- sklearn
- matplotlib
- Trading data (the bigger the better!)
**The algorithm is optimized for foreign exchange pairs currently, expect mixed results on indexes or commodities**

