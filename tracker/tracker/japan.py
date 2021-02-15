import re
from datetime import datetime

import pytz
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
space = '(?:\xe3|\x80|\\u3000)'
match_box = re.compile(('<div style="text-align:left">'
                        r'\**([0-9]*){space}'  # 名次
                        # 販売（不知道是什么），前回比
                        r'\**([0-9]*)\(?\+?\**([0-9]*)\)?{space}'
                        r'\**([0-9]*)\((.*)\){space}'  # 座席(消化率)
                        r'\**([0-9.]*)%*{space}'  # 先周比
                        r'\**([0-9.]*)%*{space}'  # 95分率
                        r'\**([0-9]*){space}'  # 全日推定
                        '(.*)'  # 映画作品名
                        '</div>'
                        ).format(space=space))

match_update_time = re.compile((
    '<B>([0-9]+)/([0-9]+)/([0-9]+)'  # Date
    '.*'
    '?([0-9]+):([0-9]+)'  # Time
    '更新'))


def get_box():
    resp = requests.get(base_url, headers=fake_headers, timeout=10)
    resp = resp.content.decode("utf-8")
    # with open("japan.html", "w", encoding="utf-8")as f:
    #     f.write(resp)
    # with open("japan.html", "r", encoding="utf-8") as f:
    #     resp = f.read()
    date_time = match_update_time.findall(resp)
    all_movies_box = match_box.findall(resp)
    return date_time, all_movies_box


def fetch():
    update_time, full_info = get_box()
    year, month, day, hour, minute = update_time[0]
    japan_timezone = pytz.timezone('Japan')
    update_time = japan_timezone.localize(datetime(int(year), int(month), int(day), int(hour), int(minute)))
    update_time_timestamp = int(update_time.timestamp()) * 1000 * 1000 * 1000
    influx_data = []

    for movie in full_info:
        idx, sales, sales_inc, seat, seat_used, compare_to_last_week, percent_rate, surmise, movie_name = movie
        fields = {
            "box_office": sales,
            "seat": seat,
            "seat_used": float(seat_used) * 100,
            "compare_to_last_week": compare_to_last_week,
            "surmise": surmise
        }
        for key in list(fields):
            if not fields[key]:
                del fields[key]
        influx_data.append({
            "measurement": "japan",
            "tags": {
                "movie_name": movie_name
            },
            "time": update_time_timestamp,
            "fields": fields
        })
    return influx_data
