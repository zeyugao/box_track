import datetime

from django.apps import apps
from django.core.management.base import BaseCommand, CommandError


def fix(label, field, offset):
    app_label, model_label = label.split('.')
    try:
        app_config = apps.get_app_config(app_label)
    except LookupError as e:
        raise CommandError(str(e))

    model = app_config.get_model(model_label)

    for obj in model.objects.all():
        old_time = getattr(obj, field)
        new_time = old_time + datetime.timedelta(minutes=offset)
        setattr(obj, field, new_time)
        print(old_time, '->', new_time)
        obj.save()


class Command(BaseCommand):
    help = 'Fix the timezone error'

    def add_arguments(self, parser):
        parser.add_argument('--label', type=str)
        parser.add_argument('--field', type=str)
        parser.add_argument('--offset', type=int)

    def handle(self, *args, **kwargs):
        fix(kwargs['label'], kwargs['field'], kwargs['offset'])
