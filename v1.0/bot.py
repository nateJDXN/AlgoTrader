import signals
from config import access_token, accountID

from apscheduler.schedulers.blocking import BlockingScheduler
from oandapyV20 import API
import oandapyV20.endpoints.orders as orders
from oandapyV20.contrib.requests import MarketOrderRequest
from oanda_candles import Pair, Gran, CandleCollector, CandleClient
from oandapyV20.contrib.requests import TakeProfitDetails, StopLossDetails

'''
SIGNAL GENERATOR
    takes in a dataframe and returns the signal (<1 for sell, >1 for buy)
'''
def signal_generator(df):

    signal_list = []

    open = df.Open.iloc[-1]
    close = df.Close.iloc[-1]
    previous_open = df.Open.iloc[-2]
    previous_close = df.Close.iloc[-2]

    #add all the pattern results to the signals list
    signal_list.add(signals.engulfing_pattern(open, close, previous_open, previous_close))
    
    print(signal_list)
    
    '''
    signal = []
    signal.append(0)
    #use pattern detection on last two rows
    for i in range (1, len(dataF)):
    df = dataF[i-1:i+1] # get last two lines
    signal.append(signal_generator(df)) # append buy/sell signal
    dataF["signal"] = signal
    '''

    # returns the total score (since buy = 1, sell = -1) 
    return sum(signal_list)

# Position Size Calculator
def position_size(stop_loss):
    pip_value = 7.07339   #pip value for USD/JPY
    account_size = 100000
    risk_percentage = 3

    risk = account_size * (risk_percentage / 100)
    position = risk / stop_loss
    units = risk / (stop_loss * pip_value)

    print("Position size: $", position, ", ", units, " units")
    return position


# Get last n candles from the live market
def get_candles(n):
    client = CandleClient(access_token, real=False) # set real=True when off demo
    collector = client.get_collector(Pair.GBP_JPY, Gran.M15)
    candles = collector.grab(n)
    return candles


'''
EXECUTING ORDERS
    Stop loss calculation: Previous candle range (high - low)
    Take profit calculation: SL * SLTP ratio (2)
'''
def trading_job():
    candles = get_candles(3)
    prices = pd.DataFrame(columns=['Open', 'Close', 'High', 'Low'])

    for index, candle in enumerate(candles):
        prices.loc[index, ['Open']] = float(str(candle.bid.o))
        prices.loc[index, ['Close']] = float(str(candle.bid.c))
        prices.loc[index, ['High']] = float(str(candle.bid.h))
        prices.loc[index, ['Low']] = float(str(candle.bid.l))

    #cast prices to floats
    prices['Open'] = prices['Open'].astype(float)
    prices['Close'] = prices['Close'].astype(float)
    prices['High'] = prices['High'].astype(float)
    prices['Low'] = prices['Low'].astype(float)

    #create signal given prices dataframe
    signal = signal_generator(prices.iloc[:-1, :])

    client = API(access_token)
    #stop loss to take profit ratio
    ratio = 2
    #range of previous candle (open - close)
    range = abs(prices['High'].iloc[-2] - prices['Low'].iloc[-2])

    SLBuy = float(str(candle.bid.o)) - range
    SLSell = float(str(candle.bid.o)) + range

    TPBuy = float(str(candle.bid.o)) + range * ratio
    TPSell = float(str(candle.bid.o)) - range * ratio

    print(prices.iloc[:-1,:])
    print(TPBuy, " ", SLBuy, " ", TPSell, " ", SLSell)

    #signal = 2

    #SELL
    if signal == 1:
        marketOrder = MarketOrderRequest(instrument="USD_JPY", units=position_size(range) * -1, takeProfitOnFill=TakeProfitDetails(TPBuy).data, stopLossOnFill=StopLossDetails(SLBuy).data)
        order = orders.OrderCreate(accountID, marketOrder.data)
        req = client.request(order)
        print("Sell signal detected!")
        print(req)

    #BUY
    elif signal == 2:
        marketOrder = MarketOrderRequest(instrument="USD_JPY", units=position_size(range), takeProfitOnFill=TakeProfitDetails(TPBuy).data, stopLossOnFill=StopLossDetails(SLBuy).data)
        order = orders.OrderCreate(accountID, marketOrder.data)
        req = client.request(order)
        print("Buy signal detected!")
        print(req)

    else:
        print("No signals detected")


def main():
    try:
        scheduler = BlockingScheduler()
        #every 15 minutes during Asian + NY sessions (8am-3pm, 7pm-4am)
        scheduler.add_job(trading_job, 'cron', day_of_week='mon-fri', hour='00-09, 13-20', minute='1, 16, 31, 46', start_date='2023-12-28 08:00:00', timezone='utc')
        print("Bot starting...")
        scheduler.start()
    except KeyboardInterrupt as k:
        print("Manual Interrupt")

main()