import datetime
import json
from collections import defaultdict

import pytz
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from .models import JapanBox


@method_decorator(csrf_exempt, name='dispatch')
class GetJapanBoxView(View):
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
        for box in query:
            resp['{0:%H:%M}'.format(box.update_time+datetime.timedelta(hours=9, minutes=19))].append({
                'name': box.name,
                'sale': box.sale
            })
        return JsonResponse(data={
            'data': [
                resp,
            ]
        })
