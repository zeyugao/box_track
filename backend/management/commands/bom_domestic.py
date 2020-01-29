import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand

from backend.models import BoxOfficeMojoDomestic

DOW_map = {
    'Sunday': 0,
    'Monday': 1,
    'Tuesday': 2,
    'Wednesday': 3,
    'Thursday': 4,
    'Friday': 5,
    'Saturday': 6
}


def mojo_field_type_money_to_int(mojo_field):
    return int(re.sub('[$,]', '', mojo_field))


def scrape(url):
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, features="html.parser")
    movie_name = soup.find('h1', attrs={'class': 'a-size-extra-large'}).text
    trs = soup.find_all('tr')[1:]
    for tr in trs:
        tds = tr.find_all('td')
        date = datetime.strptime(tds[0].a.text, '%b %d, %Y').date()
        DOW = DOW_map[tds[1].text]
        daily = mojo_field_type_money_to_int(tds[3].text)
        to_date = mojo_field_type_money_to_int(tds[8].text)
        day = int(tds[9].text)
        print('Creating', movie_name, date, DOW, daily, to_date, day)

        BoxOfficeMojoDomestic.objects.create(
            movie_name=movie_name,
            day=day,
            daily=daily,
            DOW=DOW,
            date=date,
            to_date=to_date
        )


class Command(BaseCommand):
    help = 'Scrape and store the domestic box office'

    def add_arguments(self, parser):
        parser.add_argument('--url', type=str)

    def handle(self, *args, **options):
        print(scrape(options['url']))
