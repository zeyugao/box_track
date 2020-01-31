import math
import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from django.views.generic import TemplateView

from backend.models import BoxOfficeMojoDomestic


class USCompareView(TemplateView):
    template_name = 'frontend/us_cmp.html'

    dory_total = 486295561
    game_total = 424668047
    frozen_total = 400738009

    @staticmethod
    def dow_map(dow: str):
        return {
            'Sunday': 0,
            'Monday': 1,
            'Tuesday': 2,
            'Wednesday': 3,
            'Thursday': 4,
            'Friday': 5,
            'Saturday': 6
        }[dow]

    @staticmethod
    def dow_map_reverse(dow: int):
        return [
            '星期天',
            '星期一',
            '星期二',
            '星期三',
            '星期四',
            '星期五',
            '星期六'
        ][dow]

    @staticmethod
    def format_money(money):
        money = int(money)
        abs_money = math.fabs(money)
        if abs_money < 1e3:
            return '$%d' % money
        elif abs_money < 1e6:
            return '$%.2fK' % (money / 1e3)
        elif abs_money < 1e9:
            return '$%.2fM' % (money / 1e6)
        elif abs_money < 1e12:
            return '$%.2fB' % (money / 1e9)

    @staticmethod
    def display_date(start, end):
        date_format = '%-m/%-d/%Y %a'

        def f(date):
            return date.strftime(date_format)

        return f(start[0]) if start[0] == end[0] else '从 %s 到 %s' % (f(start[0]), f(end[0]))

    @staticmethod
    def display_date_of_week(start, end):
        return start[1] if start[0] == end[0] else '第一天是%s, 最后一天是%s' % (start[1], end[1])

    @staticmethod
    def mojo_field_type_money_to_int(mojo_field):
        return int(re.sub('[$,]', '', mojo_field))

    def get_movie_data(self, movie_name: str, start: int, end: int):
        query_res = BoxOfficeMojoDomestic.objects \
            .filter(movie_name=movie_name) \
            .filter(day__gte=start, day__lte=end) \
            .order_by('day')
        days_total = 0
        total_stands = 0
        first_day = ()
        last_day = ()
        for box in query_res:
            days_total += box.daily
            total_stands = box.to_date
            first_day = first_day or (box.date, self.dow_map_reverse(box.DOW))
            last_day = (box.date, self.dow_map_reverse(box.DOW))
        return days_total, total_stands, first_day, last_day

    def parse(self, url: str, day_start, day_end, offset):
        movie = requests.get(url)
        soup = BeautifulSoup(movie.text, features="html.parser")
        days = soup.find_all('tr')

        if day_start and day_end:
            day_start = int(day_start)
            day_end = int(day_end)
        elif not day_start and not day_end:
            if not offset:
                offset = 0
            day_end = len(days) - 1
            day_start = day_end - int(offset)
        elif not day_start or not day_end and offset:
            if day_start:
                day_start = int(day_start)
                day_end = day_start + int(offset)
            else:
                day_end = int(day_end)
                day_start = day_end - int(offset)
        else:
            day_start = day_end = len(days) - 1

        days = days[day_start:day_end + 1]
        days_total = 0
        total_stands = 0
        estimated = False
        first_day = ()
        last_day = ()
        for day in days:
            if day.get('class') and 'mojo-annotation-isEstimated' in day.get('class'):
                estimated = True
            data = day.find_all('td')
            days_total += self.mojo_field_type_money_to_int(data[3].text)
            total_stands = max(total_stands, self.mojo_field_type_money_to_int(data[8].text))

            # Get date
            a = day.find_all('a')
            first_day = first_day or (
                datetime.strptime(a[0].text, '%b %d, %Y').date(), self.dow_map_reverse(self.dow_map(a[1].text)))
            last_day = (datetime.strptime(a[0].text, '%b %d, %Y').date(), self.dow_map_reverse(self.dow_map(a[1].text)))
        return (int(days_total), int(total_stands), first_day, last_day, estimated), day_start, day_end

    def get(self, request, *args, **kwargs):
        if request.GET.get('format') == '2':
            self.template_name = 'frontend/us_cmp2.html'
        return super().get(request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        day_start = self.request.GET.get('start')
        day_end = self.request.GET.get('end')
        offset = self.request.GET.get('offset')

        frozen2_url = 'https://www.boxofficemojo.com/release/rl2424210945'
        frozen2, day_start, day_end = self.parse(frozen2_url, day_start, day_end, offset)
        frozen = self.get_movie_data('Frozen', day_start, day_end)
        dory = self.get_movie_data('Finding Dory', day_start, day_end)
        hunger_game = self.get_movie_data('The Hunger Games: Catching Fire', day_start, day_end)
        context.update(
            days_range='第%d天' % day_start if day_start == day_end else '第%d到第%d天' % (day_start, day_end),
            frozen2_date=self.display_date(frozen2[2], frozen2[3]),
            frozen2_date_of_week=self.display_date_of_week(frozen2[2], frozen2[3]),
            estimated='粗报' if frozen2[4] else '精报',
            frozen2_daily=self.format_money(frozen2[0]),
            frozen2_total_due=self.format_money(frozen2[1]),

            dory_date=self.display_date(dory[2], dory[3]),
            dory_date_of_week=self.display_date_of_week(dory[2], dory[3]),
            dory_daily=self.format_money(dory[0]),
            dory_total_due=self.format_money(dory[1]),
            gap_frozen2_dory=self.format_money(dory[1] - frozen2[1]),
            gap_frozen2_dory_more_or_less='减小' if frozen2[0] > dory[0] else '增大',
            gap_frozen2_dory_diff=self.format_money(int(math.fabs(frozen2[0] - dory[0]))),
            dory_remain=self.format_money(self.dory_total - dory[1]),
            dory_total=self.format_money(self.dory_total),

            game_date=self.display_date(hunger_game[2], hunger_game[3]),
            game_date_of_week=self.display_date_of_week(hunger_game[2], hunger_game[3]),
            game_daily=self.format_money(hunger_game[0]),
            frozen2_times_game='%.2f' % (frozen2[0] / hunger_game[0]),
            game_total_due=self.format_money(hunger_game[1]),
            game_remain=self.format_money(self.game_total - hunger_game[1]),
            game_total=self.format_money(self.game_total),

            frozen_date=self.display_date(frozen[2], frozen[3]),
            frozen_date_of_week=self.display_date_of_week(frozen[2], frozen[3]),
            frozen_daily=self.format_money(frozen[0]),
            frozen_total_due=self.format_money(frozen[1]),
            frozen_remain=self.format_money(self.frozen_total - frozen[1]),
            frozen_total=self.format_money(self.frozen_total),
        )

        return context
