from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from .models import JapanBox
from django.utils import timezone
from datetime import datetime
import pytz


class GetJapanBoxView(View):
    def get(self, request, *args, **kwargs):
        now = timezone.now()
        frozen_box = JapanBox.objects.filter(
            update_time__gt=datetime(now.year, now.month, now.day, tzinfo=pytz.timezone('UTC')))

        frozen_resp = {}
        for box in frozen_box:
            frozen_resp[str(box.update_time)] = box.frozen_box[1]
        return JsonResponse(data={
            'data': [
                frozen_resp,
            ]
        })
