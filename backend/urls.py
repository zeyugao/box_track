from django.urls import path
from .views import GetJapanBoxApi, UpdateBoxApi, DumpDataApi

urlpatterns = [
    path('japan_box', GetJapanBoxApi.as_view(), name='get_japan_box'),
    path('update', UpdateBoxApi.as_view(), name='update_box'),
    path('dump', DumpDataApi.as_view(), name='dump_data')
]
