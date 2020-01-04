import datetime
import json
import random
import time
from collections import defaultdict

import pytz
import requests
from bs4 import BeautifulSoup
from django.apps import apps
from django.core import serializers
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from _thread import start_new_thread
from backend.management.commands.japan import scrape as scrape_japan
from backend.management.commands.maoyan import scrape as scrape_maoyan

from .models import JapanBox


@method_decorator(csrf_exempt, name='dispatch')
class UpdateBoxApi(View):
    def get(self, request, *args, **kwargs):
        start_new_thread(scrape_japan, (int(request.GET.get('nodelay') or 0),))
        start_new_thread(scrape_maoyan, ())
        return HttpResponse('done')


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

        resp = HttpResponse(data.encode())
        resp['Content-Type'] = 'text/plain'
        resp['Content-Disposition'] = 'attachment; filename="%s"' % (
            label+'.json')

        return resp


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
            .filter(update_time__gt=datetime.datetime(now.year, now.month, now.day, tzinfo=pytz.timezone('Japan')))

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

        query = query.order_by('update_time')

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


class AnimatedBoxOffice(View):
    def get(self, request, *args, **kwargs):
        resp = requests.get(('https://www.the-numbers.com/box-office-records/'
                             'worldwide/all-movies/cumulative/all-time-animated'))
        soup = BeautifulSoup(resp.text, features="html.parser")
        http = '''<html>
<body>
%s
</body>
</html>
'''
        return HttpResponse(http % str(soup.find('div', attrs={'id': 'main'}).find('center')))
