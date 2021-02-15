import requests
import re
from .db import client

URL = 'https://piaofang.maoyan.com/getBoxList?date=1&isSplit=true'
headers = {
    'Host': 'piaofang.maoyan.com',
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36',
    'Accept': '*/*',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'Referer': 'https://piaofang.maoyan.com/box-office?ver=normal',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Cookie': '__mta=51338902.1613271347925.1613304470840.1613307308223.8',
}

unit2value = {
    '': 1,
    '万': 1_0000,
    '亿': 1_0000_0000
}


def parse_percent(per: str):
    if per.endswith('%'):
        per = per[:-1]
    if per.startswith('<'):
        per = per[1:]
    return float(per)


box_sum_pattern = re.compile(r'([0-9.]+)([亿|万]?)')


def parse_box_sum(raw_box_sum):
    num, unit = box_sum_pattern.search(raw_box_sum).groups()
    return float(num) * unit2value[unit]


def fetch():
    resp = requests.get(URL, headers=headers)
    data = resp.json()

    if not data.get('status'):
        return False

    data = data['boxOffice']
    if not data['success']:
        return False
    data = data['data']

    update_time = data['updateInfo']['updateTimestamp']  # ms
    national_box_num = data['nationalBox']['num']
    national_box_unit = data['nationalBox']['unit']
    national_box = national_box_num * unit2value[national_box_unit]

    influx_data = [{
        "measurement": "national_sum",
        "tags": {"src": "maoyan"},
        "time": update_time,
        "fields": {
            "box_office": national_box
        }
    }]
    for movie in data['list']:
        box_office = float(movie['boxDesc'])
        box_rate = parse_percent(movie['boxRate'])
        seat_count_rate = parse_percent(movie['seatCountRate'])
        show_count_rate = parse_percent(movie['showCountRate'])
        sum_box_desc = parse_box_sum(movie['sumBoxDesc'])
        movie_name = movie['movieInfo']['movieName']

        influx_data.append({
            "measurement": "maoyan",
            "tags": {
                "movie_name": movie_name
            },
            "time": update_time,
            "fields": {
                "box_office": box_office,
                "box_rate": box_rate,
                "seat_count_rate": seat_count_rate,
                "show_count_rate": show_count_rate,
                "sum_box_desc": sum_box_desc
            }
        })

    client.write_points(influx_data, time_precision="ms")
