from django.urls import path
from .views import GetJapanBoxView
urlpatterns = [
    path('japan_box/', GetJapanBoxView.as_view(), name='api_japan_box'),
]
