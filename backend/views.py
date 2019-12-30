import datetime
import json
from collections import defaultdict

import pytz
from django.apps import apps
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from backend.management.commands.scrape import main as scrape_japan
from .models import JapanBox
from _thread import start_new_thread
import time
from django.core import serializers
import random

last_state = ''


def scrape_japan_with_delay(no_delay):
    global last_state
    last_state = scrape_japan(no_delay)


@method_decorator(csrf_exempt, name='dispatch')
class UpdateBoxApi(View):
    def get(self, request, *args, **kwargs):
        global last_state
        start_new_thread(scrape_japan_with_delay,
                         (int(request.GET.get('nodelay') or 0),))
        return JsonResponse({
            'last_state': last_state
        })


class DumpDataApi(View):
    def get(self, request, *args, **kwargs):
        dump_format = request.GET.get('format') or 'json'
        if not dump_format in ['xml', 'json', 'yaml']:
            return JsonResponse({
                'msg': 'Unsupported dump format'
            })
        label = request.GET.get('app')
        if not label:
            return JsonResponse({
                'msg': 'app label required'
            })
        try:
            app_label, model_label = label.split('.')
            app_config = apps.get_app_config(app_label)
            model = app_config.get_model(model_label)
        except Exception as e:
            return JsonResponse({
                'msg': str(e)
            })

        data = serializers.serialize(dump_format, model.objects.all())
        return JsonResponse({
            'data': data
        })


@method_decorator(csrf_exempt, name='dispatch')
class GetJapanBoxApi(View):
    def post(self, request, *args, **kwargs):
        try:
            post_data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse(data={
                'data': []
            })
        now = timezone.now()
        query = JapanBox.objects \
            .filter(update_time__gt=datetime.datetime(now.year, now.month, now.day, tzinfo=pytz.timezone('UTC')))\

        if post_data.get('name'):
            query_filter = None
            for q in post_data['name']:
                if query_filter is None:
                    query_filter = Q(name__startswith=q)
                else:
                    query_filter = query_filter | Q(name__startswith=q)
            query = query.filter(query_filter)
        elif post_data.get('rank'):
            query_filter = None
            for q in post_data['rank']:
                if query_filter is None:
                    query_filter = Q(rank=q)
                else:
                    query_filter = query_filter | Q(rank=q)
            query = query.filter(query_filter)
        else:
            return JsonResponse(data={
                'data': []
            })

        resp = defaultdict(list)
        names = set()
        for box in query:
            # resp['{0:%H:%M}'.format(box.update_time+datetime.timedelta(hours=9, minutes=19))].append({
            resp[str(box.update_time)].append({
                'name': box.name,
                'sale': box.sale
            })
            names.add(box.name)

        return JsonResponse(data={
            'names': list(names),
            'data': [
                resp,
            ]
        })
