import locale
import math
import re

import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand


def mojo_field_type_money_to_int(mojo_field):
    return int(re.sub('[$,]', '', mojo_field))


def parse(url, day_start, day_end):
    movie = requests.get(url)
    soup = BeautifulSoup(movie.text, features="html.parser")
    days = soup.find_all('tr')[day_start:day_end + 1]

    days_total = 0
    total_stands = 0
    for day in days:
        data = day.find_all('td')
        days_total += mojo_field_type_money_to_int(data[3].text)
        total_stands = max(total_stands, mojo_field_type_money_to_int(data[8].text))
    return int(days_total), int(total_stands)


def get_total_days():
    movie = requests.get('https://www.boxofficemojo.com/release/rl2424210945')
    soup = BeautifulSoup(movie.text, features="html.parser")
    return len(soup.find_all('tr')) - 1


dory_total = 486295561
hunger_total = 424668047
frozen_total = 400738009

text = '''在%s
冰2 北美 %s，Total %s

同期
多莉 %s，Total %s。同期差距 %s。%s差距 %s。
多莉余量 %s

饥饿游戏2 %s，冰2为其 %s 倍，Total %s。
饥饿游戏余量 %s

冰1 %s，Total %s。
冰1余量 %s
'''

text_as_html = '''<html>
<body>
<p>在%s</p>
<p>冰2 北美 %s，Total %s</p>
<br />
<p>同期</p>
<p>多莉 %s，Total %s。同期差距 %s。%s差距 %s。</p>
<p>多莉余量 %s</p>
<br />
<p>饥饿游戏2 %s，冰2为其 %s 倍，Total %s。</p>
<p>饥饿游戏余量 %s</p>
<br />
<p>冰1 %s，Total %s。</p>
<p>冰1余量 %s</p>
</body>
</html>'''

def format_money(money):
    money = int(money)
    if money < 1e3:
        return '$%d' % money
    elif money < 1e6:
        return '$%.2fK' % (money / 1e3)
    elif money < 1e9:
        return '$%.2fM' % (money / 1e6)
    elif money < 1e12:
        return '$%.2fB' % (money / 1e9)


def scrape(day_start=None, day_end=None, day_offset=None, as_html=False):
    if not day_start and not day_end and not day_offset:
        day_start = day_end = get_total_days()
    elif day_start and day_end:
        pass
    elif not day_offset is None and day_offset < 0:
        if day_end:
            day_start = day_end + day_offset
        else:
            day_end = get_total_days()
            day_start = day_end + day_offset
    elif not day_offset is None and day_offset > 0:
        if day_start:
            day_end = day_start + day_offset
        else:
            day_start = get_total_days()
            day_end = day_start + day_offset
    else:
        day_start = day_end = get_total_days()
    frozen = parse('https://www.boxofficemojo.com/release/rl357926401', day_start, day_end)
    frozen2 = parse('https://www.boxofficemojo.com/release/rl2424210945', day_start, day_end)
    hunger_game2 = parse('https://www.boxofficemojo.com/release/rl2638775809', day_start, day_end)
    finding_dory = parse('https://www.boxofficemojo.com/release/rl3764946433', day_start, day_end)

    locale.setlocale(locale.LC_ALL, 'en_US.utf-8')
    # format_money = partial(locale.currency, grouping=True)
    resp = (text_as_html if as_html else text) % (
        # First line, day
        '第%d天' % day_start if day_start == day_end else '第%d到第%d天' % (day_start, day_end),
        # Second line, Frozen II
        format_money(frozen2[0]), format_money(frozen2[1]),
        # Third line, Finding Dory
        format_money(finding_dory[0]), format_money(finding_dory[1]), format_money(finding_dory[1] - frozen2[1]),
        '减小' if frozen2[0] > finding_dory[0] else '增大', format_money(int(math.fabs(frozen2[0] - finding_dory[0]))),
        format_money(dory_total - finding_dory[1]),
        # Forth line, Hunger Game 2
        format_money(hunger_game2[0]), str('%.2f' % (frozen2[0] / hunger_game2[0])), format_money(hunger_game2[1]),
        format_money(hunger_total - hunger_game2[1]),
        # Fifth line, Frozen
        format_money(frozen[0]), format_money(frozen[1]),
        format_money(frozen_total - frozen[1]),
    )
    return resp


class Command(BaseCommand):
    help = 'Compare the US box'

    def add_arguments(self, parser):
        parser.add_argument('--daystart', type=int, nargs='?', default=None)
        parser.add_argument('--dayend', type=int, nargs='?', default=None)

    def handle(self, *args, **options):
        print(scrape(options['daystart'], options['dayend']))
