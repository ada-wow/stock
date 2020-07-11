import requests

headers = {
    'Host': 'xueqiu.com',
    'Referer': 'https://xueqiu.com/hq',
    'X-Requested-With': 'XMLHttpRequest',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
    'Cookie': 'xq_a_token=ad923af9f68bb6a13ada0962232589cea11925c4;'
}

base_url = 'https://xueqiu.com/service/v5/stock/screener/screen?category=CN&size=1000&order=desc&order_by=follow&only_count=0&page=1&_=1594221542488'

res = requests.get(base_url, headers = headers)
print(res.json())
