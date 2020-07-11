from urllib import request
import re

URL = 'http://fund.eastmoney.com/company/default.html'

response = request.urlopen(URL)
html = response.read()
content = html.decode('utf-8')
companies = re.findall(r'<td.*?class=.*?><a href="/Company/(.*?).html">(.*?)</a></td>', content)

for code, item in companies:
  print(code, item)
  break
# print(content)