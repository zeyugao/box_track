from django.core.management.base import BaseCommand


def exception_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e)
            return str(e)

    return wrapper


class Command(BaseCommand):
    def handle(self, *args, **options):
        raise RuntimeError('No such command')
