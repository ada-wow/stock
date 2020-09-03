# from urllib import request
# import re

# URL = 'http://fund.eastmoney.com/company/default.html'
# TESTURL = 'http://data.eastmoney.com/hsgtcg/StockInstitutionDetail.aspx?stock=002230&jgCode=B01161&jgName=UBS%20SECURITIES%20HONG%20KONG%20LTD'

# response = request.urlopen(URL)
# html = response.read()
# content = html.decode('utf-8')
# companies = re.findall(r'<td.*?class=.*?><a href="/Company/(.*?).html">(.*?)</a></td>', content)

# for code, item in companies:
#   print(code, item)
#   break
# print(content)

from bs4 import BeautifulSoup

import requests

response = requests.get('http://data.eastmoney.com/hsgtcg/StockInstitutionDetail.aspx?stock=002230&jgCode=B01161&jgName=UBS%20SECURITIES%20HONG%20KONG%20LTD')

# response.encoding = 'utf-8'

soup = BeautifulSoup(response.text, 'html.parser')

target = soup.select('table[id="tb_cgmx"]')

print(target)