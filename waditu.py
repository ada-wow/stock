# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import tushare as ts
import pandas as pd
import re
import json
import datetime

TOKEN = 'dbe99edca3e7707bf22f5323bb4e65331cfffbb57cc47be2e407b7e5'
# pro接口需要token
pro = ts.pro_api(TOKEN)
# 获取股票列表代码
stock_list = pro.query('stock_basic', fields='ts_code')

def date_range(begin, end = datetime.date.today()):
  array = []
  for i in range((end - begin).days + 1):
    day = begin + datetime.timedelta(days = i)
    array.append(day.strftime('%Y-%m-%d'))
  return array

dates = date_range(datetime.date(2020, 07, 04))

def stock_code_format(code):
  return re.sub(r'.\w+$', '', code)

# 历史大单交易数据
def get_plenty_of_order():
  # 笔数阀值
  vol = 1000
  for index, date in enumerate(dates):
    for i in range(len(stock_list)):
      target_stock = stock_list.loc[i]
      if i <= 2:
        target_date_stock = ts.get_sina_dd(stock_code_format(target_stock['ts_code']), date=date, vol=vol)
        if target_date_stock is not None:
          print(target_date_stock, date)

# 历史异常交易数据
def get_exception_of_order():
  # 异常单倍数阀值
  threshold = 5 
  result = []
  for i in range(len(stock_list)):
    target_stock = stock_list.loc[i]
    if i <= 2:
      for date in dates:
        target_date_stock = ts.get_tick_data(stock_code_format(target_stock['ts_code']), date=date, src='tt')
        if target_date_stock is not None:
          # 拿第一天的change均值作为后面参考值
          average_change = 0
          total_change = 0
          total_change_count = 0
          # if index == 0:
          for i in range(len(target_date_stock)):
            change = abs(float(target_date_stock.loc[i]['change']))
            if change > 0:
              total_change += change
              total_change_count += 1
          average_change = total_change / total_change_count
          for i in range(len(target_date_stock)):
              change = abs(float(target_date_stock.loc[i]['change']))
              if change >= average_change * threshold:
                print(target_date_stock.loc[i])
            


get_exception_of_order()
# get_plenty_of_order()

# fund = ts.fund_holdings(2020, 1)
# print(fund)
