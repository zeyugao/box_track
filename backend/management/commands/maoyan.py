import json
from datetime import datetime

import pytz
import requests
from django.core.management.base import BaseCommand
from django.utils import timezone
from backend.models import Maoyan, MaoyanFull
from .utils import exception_handler

fake_headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Cookie': '_lxsdk_cuid=16ebad3f532c8-02d492d3ccd81f-2393f61-144000-16ebad3f533c8; _lxsdk=02C3E080133411EABA62AF3DF39ADBD64D54C30C98AC4FB4B79D96212D28AFE8; __mta=55334292.1575092498986.1575202284804.1575202342428.5; __mta=55334292.1575092498986.1575202342428.1577870150927.6',
    'Connection': 'keep-alive',
    'DNT': '1',
    'Host': 'piaofang.maoyan.com',
    'Referer': 'https://piaofang.maoyan.com/dashboard?movieId=247949',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
}
url = 'https://piaofang.maoyan.com/second-box'

fix_type = {
    'avgSeatView': lambda x: float(x.replace('%', '').replace('<', '')),
    'avgShowView': int,
    'avgViewBox': float,
    'boxInfo': float,
    'boxRate': lambda x: float(x.replace('%', '').replace('<', '')),
    'movieId': lambda x: x,
    'movieName': lambda x: x,
    'seatRate': lambda x: float(x.replace('%', '').replace('<', '')),
    'showInfo': int,
    'showRate': lambda x: float(x.replace('%', '').replace('<', '')),
    'sumBoxInfo': lambda x: x,
    'viewInfo': float,
    'viewInfoV2': lambda x: x
}


def get_box():
    resp = requests.get(url, headers=fake_headers)
    content = json.loads(resp.text)
    if not content['success']:
        raise ValueError('failed')
    return content['data']


@exception_handler
def scrape():
    full_info = get_box()
    hour, mintue, second = full_info['updateInfo'].replace(
        '北京时间', '').strip().split(':')
    utc_hour = (int(hour) - 8 + 24) % 24
    utc_now = timezone.now()
    update_time = datetime(utc_now.year, utc_now.month, utc_now.day,
                           utc_hour, int(mintue), int(second), tzinfo=pytz.timezone('UTC'))

    # for movie in full_info['list']:
    #    movie_info = {
    #        key: fix_type[key](movie[key])
    #        for key in [
    #            'avgSeatView',
    #            'avgShowView',
    #            'avgViewBox',
    #            'boxInfo',
    #            'boxRate',
    #            'movieId',
    #            'movieName',
    #            'seatRate',
    #            'showInfo',
    #            'showRate',
    #            'sumBoxInfo',
    #            'viewInfo',
    #            'viewInfoV2',
    #        ]
    #    }
    #    Maoyan.objects.create(update_time=update_time,
    #                          **movie_info)

    MaoyanFull.objects.create(update_time=update_time, full_info=full_info)


class Command(BaseCommand):
    help = 'Scrape the maoyan box'

    def handle(self, *args, **options):
        print(scrape())
