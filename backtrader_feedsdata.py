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
#############################################################
#global values
#############################################################
#############################################################
#global function
#############################################################
def G_get_dataframe():
     # Get a pandas dataframe
    datapath = './data/stockinfo.csv'
    tmpdatapath = './data/stockinfo_tmp.csv'
    print('-----------------------read csv---------------------------')
    dataframe = pd.read_csv(datapath,
                                skiprows=0,
                                header=0,
                                parse_dates=True,
                                index_col=0)
    print(dataframe)
    print('--------------------------------------------------')
    print('-----------------------change time------------------------')
    dataframe.trade_date =  pd.to_datetime(dataframe.trade_date, format="%Y%m%d")
    print(dataframe)
    print('--------------------------------------------------')
    print('-----------------------add openinterest-------------------')
    dataframe['openinterest'] = '0'
    print(dataframe)
    print('--------------------------------------------------')
    print('-----------------------make feedsdf-----------------------')
    feedsdf = dataframe[['trade_date', 'open', 'high', 'low', 'close', 'vol', 'openinterest']]
    print(feedsdf)
    print('--------------------------------------------------')
    print('-----------------------change columns---------------------')
    feedsdf.columns =['datetime', 'open', 'high', 'low', 'close', 'volume', 'openinterest']
    print(feedsdf)
    print('--------------------------------------------------')
    print('-----------------------change index-----------------------')
    feedsdf.set_index(keys='datetime', inplace =True)
    print(feedsdf)
    print('--------------------------------------------------')
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
    # Create a cerebro entity
    cerebro = bt.Cerebro(stdstats=False)

    # Add a strategy
    cerebro.addstrategy(bt.Strategy)

    # Get a pandas dataframe
    feedsdf = G_get_dataframe()
    
    # Pass it to the backtrader datafeed and add it to the cerebro
    data = bt.feeds.PandasData(dataname=feedsdf)
    print(data)

    cerebro.adddata(data)

    # Run over everything
    cerebro.run()

    # Plot the result
    cerebro.plot(style='bar')

