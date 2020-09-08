
### 雪球（网页端）关注人数排行榜

接口地址

```
https://xueqiu.com/service/v5/stock/screener/screen?category=CN&size=1000&order=desc&order_by=follow&only_count=0&page=1
```

请求参数

```
size：返回的排名数量
order：正倒序
order_by：follow / follow7d (全部关注 / 7天新关注)
page：当前页码数
```

响应参数

```
current：当前股价值
pct：热度变化值
symbol：股票编号
name：股票名
follow：关注人数
```

### *new 雪球 （app端）热门搜索排行榜

接口地址

```
http://stock.xueqiu.com/v5/stock/screener/quote/list.json?market=CN&order=desc&order_by=value&page=1&size=100&type=hot_1h
```

请求参数

```
market：股票市场
order：正倒序
order_by: value / rank_change / tweet / followers （热度值 / 名次变化 / 评论数 / 关注人数）
size: 返回的排名数量
type: hot_1h / hot_24h (一小时 / 24小时)
```

响应参数

```
value：热度值
followers：总关注者
rank_change：排名升降变化
```

### *new 雪球 （app端）个股雪球当前热点查询

接口地址

```
https://api.xueqiu.com/query/v1/hot_event/symbol/tag.json?symbols=SH688981
```

请求参数

```
symbols：股票编号（支持多个，逗号隔开）
```

响应参数

```
tag：热点标签
```

### *new 雪球 （app 端）个股实时热度排行

接口地址

 ```
https://stock.xueqiu.com/v5/stock/hot/realtime.json?symbol=SH600030
 ```

请求参数

```
symbol：股票编号
```

响应参数

```
visitors：在看人数
discussions：评论数
total：排行榜总数
rank：当前该股排行数
rank_change：排名变化数
rank_history：排行历史数据
rank_tag：排行热门标签
```

### 雪球 （app端）个股大事件提醒 时间轴事件

接口地址

```
https://stock.xueqiu.com/v5/stock/screener/event/list.json?page=1&size=999&symbol=SH600030
```

请求参数

```
size：请求一页数量
symbol：股票编号
```

响应参数

```
title：大事件标题
message：大事件具体描述及数据简介（当中数据可以提取）
```

### 雪球 （app 端）个股十大股东&流通股东

接口地址

```
https://stock.xueqiu.com/v5/stock/f10/cn/top_holders.json?circula=1&symbol=SH600030&&locate=1553961600000
```

请求参数

```
symbol：股票编号
locate: 时间戳（不传的话默认系统最新时间戳）
circula：固定资产周转率 1为流通股东 0为股东
```

响应参数

```
items: [
	{
		chg：持仓变化数，
		held_num：持股数，
		held_ratio：持股比例
		holder_name：持股人/机构
	}
]
quit: [
  {
    held_num: 上期持股
    held_ratio: 上期占比
    holder_rank: 上期排名
    holder_name: 股东名字
  }
]
time: [
  {
    name: 名字
    value: 时间戳 （上面locate参数可由此字段获取请求）
  }
]
```

### 雪球 （app 端）个股机构持仓

接口地址

```
https://stock.xueqiu.com/v5/stock/f10/cn/org_holding/detail.json?count=50&symbol=SH601216&timestamp=1585584000000
```

请求参数

```
count: 展示数量
timestamp: 时间戳（不传的话默认系统最新时间戳）
symbol: 股票编号
```

响应参数

```
all_items: 全部
fund_items: 基金
social_items：社保
other_items：其他
qfii_items： QGII
insurance_items：保险
broker_items：券商
time: [
  {
    name: 名字
    value: 时间戳 （上面locate参数可由此字段获取请求）
  }
]
```









### 同花顺 （网页端）个股热度

接口地址

```
https://eq.10jqka.com.cn/earlyInterpret/index.php?con=index&act=getIndexData&stockCode=600196&date=20200724
```

请求参数

```
stockCode：股票编号
date：请求的具体日期
```

响应参数

```
stockInfo: {
	price： 股价
	hotRank：人气排行数
}
```

### 东财（网页端）QFII个股持仓

接口地址

```
http://dcfm.eastmoney.com/em_mutisvcexpandinterface/api/js/get?type=HSGTSHHDDET&token=70f12f2f4f091e459a279469fe49eca5&filter=(SCODE='000651')(PARTICIPANTCODE='B01110')

```

请求参数

```
type：HSGTSHHDDET / HSGTHHDDET （意义不明，二选一）
token：网页token （需要js脚本里取出）
SCODE：股票代号
PARTICIPANTCODE：机构代号
```

响应参数

```
HDDATE：时间
SCODE：股票代号
SNAME：股票名
PARTICIPANTCODE：机构代号
PARTICIPANTNAME：机构名
SHAREHOLDSUM：持股数量
SHARESRATE：持股占a股百分比
CLOSEPRICE：当天收盘价
ZDF：当天涨跌
SHAREHOLDPRICE：持股市值
SHAREHOLDPRICEONE：一日市值变化
SHAREHOLDPRICEFIVE：五日市值变化
SHAREHOLDPRICETEN：十日市值变化
MARKET：
ShareHoldSumChg：
```

### 东财（网页端）QFII持仓汇总

接口地址

```
http://dcfm.eastmoney.com//em_mutisvcexpandinterface/api/js/get?token=70f12f2f4f091e459a279469fe49eca5&st=HDDATE,SHAREHOLDPRICE&sr=3&p=1&ps=50&js=var%20KxzmAGva={pages:(tp),data:(x)}&filter=(PARTICIPANTCODE=%27C00019%27)(MARKET%20in%20(%27001%27,%27003%27))(HDDATE=^2020-09-01^)&type=HSGTNHDDET&rt=53301871

```

请求参数

```
type：HSGTSHHDDET / HSGTHHDDET （意义不明，二选一）
token：网页token （需要js脚本里取出）
HDDATE：日期
PARTICIPANTCODE：机构代号
```

响应参数

```
HDDATE：时间
SCODE：股票代号
SNAME：股票名
PARTICIPANTCODE：机构代号
PARTICIPANTNAME：机构名
SHAREHOLDSUM：持股数量
SHARESRATE：持股占a股百分比
CLOSEPRICE：当天收盘价
ZDF：当天涨跌
SHAREHOLDPRICE：持股市值
SHAREHOLDPRICEONE：一日市值变化
SHAREHOLDPRICEFIVE：五日市值变化
SHAREHOLDPRICETEN：十日市值变化
MARKET：
ShareHoldSumChg：
```

### 东财（网页端）每日机构统计

接口地址

```
http://dcfm.eastmoney.com//em_mutisvcexpandinterface/api/js/get?type=HSGTCOMSTA&token=70f12f2f4f091e459a279469fe49eca5&st=HDDATE,SHAREHOLDCOUNT&sr=3&p=1&ps=50&js=var%20bnPRsJom={pages:(tp),data:(x)}&filter=(MARKET=%27N%27)(HDDATE=^2020-09-01^)&rt=53301895

```

请求参数

```
type：HSGTCOMSTA
token：网页token （需要js脚本里取出）
HDDATE：日期
```

响应参数

```
HDDATE：时间
PARTICIPANTCODE：机构代号
PARTICIPANTNAME：机构名
SHAREHOLDSUM：持股数量
SHARESRATE：持股占a股百分比
CLOSEPRICE：当天收盘价
ZDF：当天涨跌
SHAREHOLDPRICE：持股市值
SHAREHOLDPRICEONE：一日市值变化
SHAREHOLDPRICEFIVE：五日市值变化
SHAREHOLDPRICETEN：十日市值变化
MARKET：
ShareHoldSumChg：
```
