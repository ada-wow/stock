
import requests

if __name__ == '__main__':
    # url = "http://guba.eastmoney.com/interface/GetData.aspx"
    # data = {
    #     "param":"code = 601519",
    #     "path": "webarticlelist/api/guba/ gubainfo",
    #     "env": "2"
    # }
    # resp = requests.post(url=url, data=data)
    # print(resp.text)
    url = "https://stock.xueqiu.com/v5/stock/hot_stock/list.json?size=999&_type=10&type=10"

    resp = requests.get(url=url)
    for item in resp.json():
        if item['increment' > 5]:
            print item