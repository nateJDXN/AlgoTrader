from backtesting import Strategy
from backtesting.test import GOOG
from backtesting.lib import crossover
import talib

#print(GOOG)

'''
ENGULFING PATTERN
    Occurs when a larger candlestick fully 'engulfs' the previous, smaller candlestick 
    indicating a potential trend reversal. It's considered bullish if a bullish candle 
    engulfs a bearish candle signaling upward momentum, and vice versa.
'''
def engulfing_pattern(open, close, previous_open, previous_close):
  #Bearish pattern
  if open > close and previous_open < previous_close and close < previous_open and open >= previous_close:
    return -1  # sell signal

  #Bullish pattern
  elif open < close and previous_open > previous_close and close > previous_open and open <= previous_close:
    return 1  # buy signal

  #No clear pattern
  else:
    return 0
  

'''
BREAKOUT PATTERN
    - Identifies 3 "bounces" determined by ceiling and support zones
    - Width of the zone is included as well and can be fined tuned
    - Breakout indetified if a candle closes above/below zone(s)

'''




