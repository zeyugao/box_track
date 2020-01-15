import random
import re
import time
from datetime import datetime

import pytz
import requests
from django.core.management.base import BaseCommand
from django.utils import timezone

from backend.models import JapanBox, JapanBoxFull
from .utils import exception_handler

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
                        '\**([0-9]*){space}'  # 名次
                        # 販売（不知道是什么），前回比
                        '\**([0-9]*)\(?\+?\**([0-9]*)\)?{space}'
                        '\**([0-9]*)\((.*)\){space}'  # 座席(消化率)
                        '\**([0-9\.]*)%*{space}'  # 先周比
                        '\**([0-9\.]*)%*{space}'  # 95分率
                        '\**([0-9]*){space}'  # 全日推定
                        '(.*)'  # 映画作品名
                        '</div>'
                        ).format(space=space))

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


@exception_handler
def scrape(no_delay):
    if not no_delay:
        time.sleep(random.randint(10, 300) + random.random())
    update_time, full_info = get_box()
    if not full_info:
        raise ValueError('Failed to match the info')
    year, month, day, hour, minute = update_time[0]
    now_time = timezone.now()
    japan_timezone = pytz.timezone('Japan')
    update_time = japan_timezone.localize(datetime(int(year), int(month), int(day), int(hour), int(minute)))
    if JapanBoxFull.objects.filter(update_time=update_time).exists():
        print(update_time, 'exists')
        return str(update_time) + ' ' + 'exists'

    for box_info in full_info:
        extra_info = {
            desp: box_info[i] or -1
            for i, desp in enumerate([
                'rank',
                'sale',
                'sale_inc',
                'seat',
                'seat_used',
                'rate_last_week',
                'rate_95',
                'estimation',
                'name'
            ])
        }

        JapanBox.objects.create(
            update_time=update_time,
            **extra_info
        )
    JapanBoxFull.objects.create(
        update_time=update_time,
        store_time=now_time,
        full_info=full_info
    )
    return 'Succeed'


class Command(BaseCommand):
    help = 'Scrape the japan box'

    def add_arguments(self, parser):
        parser.add_argument('--nodelay', action='store_true')

    def handle(self, *args, **options):
        print(scrape(options['nodelay']))
