import datetime
from _thread import start_new_thread
from ast import literal_eval
from collections import defaultdict
from datetime import datetime

import pytz
import requests
from bs4 import BeautifulSoup
from django.apps import apps
from django.core import serializers
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from backend.management.commands.japan import scrape as scrape_japan
from backend.management.commands.maoyan import scrape as scrape_maoyan
from .models import JapanBoxFull


@method_decorator(csrf_exempt, name='dispatch')
class UpdateBoxApi(View):
    def get(self, request, *args, **kwargs):
        start_new_thread(scrape_japan, (int(request.GET.get('nodelay') or 0),))
        start_new_thread(scrape_maoyan, ())
        return HttpResponse('done')


class DumpDataApi(View):
    def get(self, request, *args, **kwargs):
        dump_format = request.GET.get('format') or 'json'
        if dump_format not in ['xml', 'json', 'yaml']:
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
                label + '.json')

        return resp


@method_decorator(csrf_exempt, name='dispatch')
class GetJapanBoxApi(View):
    def post(self, request, *args, **kwargs):
        date_format = '%Y/%m/%d %H:%M:%S%z'
        japan_timezone = pytz.timezone('Japan')

        start_datetime = datetime.strptime(request.POST['start'], date_format)
        end_datetime = datetime.strptime(request.POST['end'], date_format)
        query = JapanBoxFull.objects.filter(update_time__gte=start_datetime).filter(update_time__lte=end_datetime)
        query = query.order_by('update_time')

        result = defaultdict(list)
        names = set()
        for obj in query:
            for info in literal_eval(obj.full_info):
                for part_name in request.POST.getlist('name[]'):
                    if part_name in info[-1]:
                        result[str(obj.update_time)].append({
                            'name': info[-1],
                            'sale': info[1],
                            'rate': (float(info[5]) or 0) / 100
                        })
                        names.add(info[-1])
                        break

        return JsonResponse(data={
            'names': list(names),
            'data': result
        })


class AnimatedBoxOffice(View):
    def get(self, request, *args, **kwargs):
        resp = requests.get(('https://www.the-numbers.com/box-office-records/'
                             'worldwide/all-movies/cumulative/all-time-animated'))
        soup = BeautifulSoup(resp.text, features="html.parser")
        http = '''<html>
<body>
<table>
<tbody>
%s
</tbody>
</table>
</body>
</html>
'''
        all_list = soup.find('div', attrs={'id': 'main'}).find('center')
        tbody = all_list.find('tbody')
        top_two = tbody.find_all('tr')[:2]
        return HttpResponse(http % ''.join(map(str, top_two)))
