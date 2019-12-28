from django.core.management.base import BaseCommand
from backend.management.commands.japan import get_box as get_ja_box
from datetime import datetime
from backend.models import JapanBox, JapanBoxFull
from django.utils import timezone
import pytz

import time
import random


def main(no_delay):
    if not no_delay:
        time.sleep(random.randint(10, 300)+random.random())
    update_time, full_info = get_ja_box()
    year, month, day, hour, mintue = update_time[0]
    now_time = timezone.now()
    update_time = datetime(int(year), int(month), int(day), int(hour), int(mintue),
                           tzinfo=pytz.timezone('Japan'))

    if JapanBoxFull.objects.filter(update_time=update_time).exists():
        print(update_time, 'exists')
        return

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


class Command(BaseCommand):
    help = 'Scrape the box'

    def add_arguments(self, parser):
        parser.add_argument('--no-delay', action='store_true')

    def handle(self, *args, **options):
        main(options['no_delay'])
