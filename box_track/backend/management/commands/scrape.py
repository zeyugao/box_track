from django.core.management.base import BaseCommand
from backend.management.commands.japan import get_box as get_ja_box
from datetime import datetime
from backend.models import JapanBox
import pytz

import time
import random


def main():
    time.sleep(random.randint(10, 300)+random.random())
    update_time, full_info = get_ja_box()
    year, month, day, hour, mintue = update_time[0]

    for box in full_info:
        if box[-1] == 'アナと雪の女王２':
            frozen_box = box

    JapanBox.objects.create(update_time=datetime(
        int(year), int(month), int(day), int(hour), int(mintue), tzinfo=pytz.timezone('Japan')), frozen_box=box, full_info=full_info)


class Command(BaseCommand):
    help = 'Scrape the box'

    def handle(self, **kwargs):
        main()
