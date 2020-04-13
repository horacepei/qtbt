# -*- coding: utf-8 -*-
"""
Created on Sun Mar 29 12:18:17 2020

@author: horace pei
"""
#############################################################
#import
#############################################################
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import os,sys
import pandas as pd
import backtrader as bt
#############################################################
#global const values
#############################################################
#############################################################
#static function
#############################################################
#############################################################
#class
#############################################################
# Create a Stratey
class TestStrategy(bt.Strategy):
    # 自定义均线的实践间隔，默认是5天
    params = (
        ('maperiod', 5),
    )
    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close
        # To keep track of pending orders
        self.order = None
        # buy price
        self.buyprice = None
        # buy commission
        self.buycomm = None
        # 增加均线，简单移动平均线（SMA）又称“算术移动平均线”，是指对特定期间的收盘价进行简单平均化
        self.sma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.maperiod)
    #订单状态改变回调方法 be notified through notify_order(order) of any status change in an order
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return
        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            elif order.issell():
               self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))
            self.bar_executed = len(self)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
        # Write down: no pending order
        self.order = None

    #交易状态改变回调方法 be notified through notify_trade(trade) of any opening/updating/closing trade
    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        # 每笔交易收益 毛利和净利
        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])
        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return
        # Check if we are in the market(当前账户持股情况，size，price等等)
        if not self.position:
            # Not yet ... we MIGHT BUY if ...
            if self.dataclose[0] >= self.sma[0]:
                #当收盘价，大于等于均线的价格
                # BUY, BUY, BUY!!! (with all possible default parameters)
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                # Keep track of the created order to avoid a 2nd order
                self.order = self.buy()
        else:
            # Already in the market ... we might sell
            if self.dataclose[0] < self.sma[0]:
                #当收盘价，小于均线价格
                # SELL, SELL, SELL!!! (with all possible default parameters)
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell()
#############################################################
#global values
#############################################################
#############################################################
#global function
#############################################################
def get_dataframe():
     # Get a pandas dataframe
    datapath = './data/stockinfo.csv'
    tmpdatapath = './data/stockinfo_tmp.csv'
    print('-----------------------read csv---------------------------')
    dataframe = pd.read_csv(datapath,
                                skiprows=0,
                                header=0,
                                parse_dates=True,
                                index_col=0)
    dataframe.trade_date =  pd.to_datetime(dataframe.trade_date, format="%Y%m%d")
    dataframe['openinterest'] = '0'
    feedsdf = dataframe[['trade_date', 'open', 'high', 'low', 'close', 'vol', 'openinterest']]
    feedsdf.columns =['datetime', 'open', 'high', 'low', 'close', 'volume', 'openinterest']
    feedsdf.set_index(keys='datetime', inplace =True)
    feedsdf.iloc[::-1].to_csv(tmpdatapath)
    feedsdf = pd.read_csv(tmpdatapath, skiprows=0, header=0, parse_dates=True, index_col=0)
    if os.path.isfile(tmpdatapath):
        os.remove(tmpdatapath)
        print(tmpdatapath+" removed!")
    return feedsdf
########################################################################
#main
########################################################################
if __name__ == '__main__':
    # Create a cerebro entity(创建cerebro)
    cerebro = bt.Cerebro()
    # Add a strategy(加入自定义策略,可以设置自定义参数，方便调节)
    cerebro.addstrategy(TestStrategy, maperiod=7)
    # Get a pandas dataframe(获取dataframe格式股票数据)
    feedsdf = get_dataframe()
    # Pass it to the backtrader datafeed and add it to the cerebro(加入数据)
    data = bt.feeds.PandasData(dataname=feedsdf)
    cerebro.adddata(data)
    # Add a FixedSize sizer according to the stake(国内1手是100股，最小的交易单位)
    cerebro.addsizer(bt.sizers.FixedSize, stake=100)
    # Set our desired cash start(给经纪人，可以理解为交易所股票账户充钱)
    cerebro.broker.setcash(10000.0)
     # Set the commission - 0.1%(设置交易手续费，双向收取)
    cerebro.broker.setcommission(commission=0.001)
    # Print out the starting conditions(输出账户金额)
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    # Run over everything(执行回测)
    cerebro.run()
    # Print out the final result(输出账户金额)
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

