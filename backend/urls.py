from django.urls import path
from .views import GetJapanBoxApi, UpdateBoxApi

urlpatterns = [
    path('japan_box', GetJapanBoxApi.as_view(), name='get_japan_box'),
    path('update', UpdateBoxApi.as_view(), name='update_japan_box')
]
