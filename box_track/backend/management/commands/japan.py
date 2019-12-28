import re

import requests

base_url = 'https://chu-mimorin.ssl-lolipop.jp/mimorin2014/rankinglist11.html'
fake_headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
    'referer': 'https://mimorin2014.blog.fc2.com/blog-category-6.html',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-encoding': 'gzip, deflate, ·br',
    'sec-fetch-mode': 'nested-navigate',
    'sec-fetch-site': 'cross-site'
}

match_box = re.compile(('<div style="text-align:left">'
                        '\**([0-9]+)\\u3000'  # 名次
                        '\**([0-9]+)\(\+\**([0-9]+)\)\\u3000'  # 販売（不知道是什么），前回比
                        '\**([0-9]+)\((.*)\)\\u3000'  # 座席(消化率)
                        '\**([0-9\.]*)%?\\u3000'  # 先周比
                        '\**([0-9\.]+)%?\\u3000'  # 95分率
                        '\**([0-9]+)\\u3000'  # 全日推定
                        '(.*)'  # 映画作品名
                        '</div>'
                        ))

match_update_time = re.compile((
    '<B>([0-9]+)/([0-9]+)/([0-9]+)'  # Date
    '.*'
    '?([0-9]+):([0-9]+)'  # Time
    '更新'))


def get_box():
    resp = requests.get(base_url, headers=fake_headers)
    resp = resp.content.decode()
    date_time = match_update_time.findall(resp)
    all_movies_box = match_box.findall(resp)
    return date_time, all_movies_box
