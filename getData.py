# -*- coding: utf-8 -*-
"""
公众号：Python疯子
作  者：大杨子Young
时  间：20180814
"""
## 调用要使用的包
import json
import random
import requests
import time
import pandas as pd

## 设置headers和cookie
header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win32; x32; rv:54.0) Gecko/20100101 Firefox/54.0',
          'Connection': 'keep-alive'}
cookies = 'v=3; iuuid=1A6E888B4A4B29B16FBA1299108DBE9CDCB327A9713C232B36E4DB4FF222CF03; webp=true; ci=1%2C%E5%8C%97%E4%BA%AC; __guid=26581345.3954606544145667000.1530879049181.8303; _lxsdk_cuid=1646f808301c8-0a4e19f5421593-5d4e211f-100200-1646f808302c8; _lxsdk=1A6E888B4A4B29B16FBA1299108DBE9CDCB327A9713C232B36E4DB4FF222CF03; monitor_count=1; _lxsdk_s=16472ee89ec-de2-f91-ed0%7C%7C5; __mta=189118996.1530879050545.1530936763555.1530937843742.18'
cookie = {}
for line in cookies.split(';'):
    name, value = cookies.strip().split('=', 1)
    cookie[name] = value

## 爬取数据，每次理论上可以爬取1.5W调数据，存在大量重复数据，需要多次执行，最后统一去重
tomato = pd.DataFrame(columns=['userId', 'nickName', 'date', 'score', 'city', 'comment'])
for i in range(0, 1000):
    j = random.randint(1, 1000)
    print(str(i) + ' ' + str(j))
    try:
        time.sleep(2)
        url = 'http://m.maoyan.com/mmdb/comments/movie/1203084.json?_v_=yes&offset=' + str(j)
        html = requests.get(url=url, cookies=cookie, headers=header).content
        data = json.loads(html.decode('utf-8'))['cmts']
        for item in data:
            tomato = tomato.append({'userId':item['userId'] , 'nickName':item['nickName'], 'date': item['time'].split(' ')[0], 'city': item['cityName'],
                                    'score': item['score'], 'comment': item['content']}, ignore_index=True)

        tomato.to_excel('./一出好戏.xlsx', index=False)
    except:
        continue