import locale
import math
import re

import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand


def mojo_field_type_money_to_int(mojo_field):
    return int(re.sub('[$,]', '', mojo_field))


def parse(url: str, day_start: int, day_end: int):
    movie = requests.get(url)
    soup = BeautifulSoup(movie.text, features="html.parser")
    days = soup.find_all('tr')[day_start:day_end + 1]

    days_total = 0
    total_stands = 0
    estimated = False
    first_day = ()
    last_day = ()
    for day in days:
        if day.get('class') and 'mojo-annotation-isEstimated' in day.get('class'):
            estimated = True
        data = day.find_all('td')
        days_total += mojo_field_type_money_to_int(data[3].text)
        total_stands = max(total_stands, mojo_field_type_money_to_int(data[8].text))

        # Get date
        a = day.find_all('a')
        first_day = first_day or (a[0].text, a[1].text)
        last_day = (a[0].text, a[1].text)
    return int(days_total), int(total_stands), first_day, last_day, estimated


def get_total_days():
    movie = requests.get('https://www.boxofficemojo.com/release/rl2424210945')
    soup = BeautifulSoup(movie.text, features="html.parser")
    return len(soup.find_all('tr')) - 1


dory_total = 486295561
hunger_total = 424668047
frozen_total = 400738009

text = '''在{days_range}
冰2
{frozen2_date}, {frozen2_date_of_week}
北美{estimated} {frozen2_daily}，Total {frozen2_total_due}

同期
多莉
{dory_date}, {dory_date_of_week}
北美 {dory_daily}，Total {dory_total_due}。同期差距 {gap_frozen2_dory}。{gap_frozen2_dory_more_or_less}差距 {gap_frozen2_dory_diff}。
多莉余量 {dory_remain}

饥饿游戏2
{game_date}, {game_date_of_week}
北美 {game_daily}，冰2为其 {frozen2_times_game} 倍，Total {game_total_due}。
饥饿游戏余量 {game_remain}

冰1
{frozen_date}, {frozen_date_of_week}
北美 {frozen_daily}，Total {frozen_total_due}。
冰1余量 {frozen_remain}
'''


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


def display_date(start, end):
    return start[0] if start[0] == end[0] else '从 %s 到 %s' % (start[0], end[0])


def display_date_of_week(start, end):
    return start[1] if start[0] == end[0] else '第一天: %s, 最后一天: %s' % (start[1], end[1])


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
    if day_start > day_end:
        return ''
    frozen = parse('https://www.boxofficemojo.com/release/rl357926401', day_start, day_end)
    frozen2 = parse('https://www.boxofficemojo.com/release/rl2424210945', day_start, day_end)
    hunger_game2 = parse('https://www.boxofficemojo.com/release/rl2638775809', day_start, day_end)
    finding_dory = parse('https://www.boxofficemojo.com/release/rl3764946433', day_start, day_end)

    locale.setlocale(locale.LC_ALL, 'en_US.utf-8')

    if as_html:
        content = '<html>\n<body>\n' + ''.join(
            ['<p>%s</p>\n' % line if line else '<br>\n' for line in text.split('\n')]) + '</body></html>'
    else:
        content = text

    # format_money = partial(locale.currency, grouping=True)
    resp = content.format(
        days_range='第%d天' % day_start if day_start == day_end else '第%d到第%d天' % (day_start, day_end),

        frozen2_date=display_date(frozen2[2], frozen2[3]),
        frozen2_date_of_week=display_date_of_week(frozen2[2], frozen2[3]),
        estimated='粗报' if frozen2[4] else '精报',
        frozen2_daily=format_money(frozen2[0]),
        frozen2_total_due=format_money(frozen2[1]),

        dory_date=display_date(finding_dory[2], finding_dory[3]),
        dory_date_of_week=display_date_of_week(finding_dory[2], finding_dory[3]),
        dory_daily=format_money(finding_dory[0]),
        dory_total_due=format_money(finding_dory[1]),
        gap_frozen2_dory=format_money(finding_dory[1] - frozen2[1]),
        gap_frozen2_dory_more_or_less='减小' if frozen2[0] > finding_dory[0] else '增大',
        gap_frozen2_dory_diff=format_money(int(math.fabs(frozen2[0] - finding_dory[0]))),
        dory_remain=format_money(dory_total - finding_dory[1]),

        game_date=display_date(hunger_game2[2], hunger_game2[3]),
        game_date_of_week=display_date_of_week(hunger_game2[2], hunger_game2[3]),
        game_daily=format_money(hunger_game2[0]),
        frozen2_times_game='%.2f' % (frozen2[0] / hunger_game2[0]),
        game_total_due=format_money(hunger_game2[1]),
        game_remain=format_money(hunger_total - hunger_game2[1]),

        frozen_date=display_date(frozen[2], frozen[3]),
        frozen_date_of_week=display_date_of_week(frozen[2], frozen[3]),
        frozen_daily=format_money(frozen[0]),
        frozen_total_due=format_money(frozen[1]),
        frozen_remain=format_money(frozen_total - frozen[1]),
    )
    return resp


class Command(BaseCommand):
    help = 'Compare the US box'

    def add_arguments(self, parser):
        parser.add_argument('--daystart', type=int, nargs='?', default=None)
        parser.add_argument('--dayend', type=int, nargs='?', default=None)
        parser.add_argument('--ashtml', action='store_true')

    def handle(self, *args, **options):
        print(scrape(day_start=options['daystart'], day_end=options['dayend'], as_html=options['ashtml']))
