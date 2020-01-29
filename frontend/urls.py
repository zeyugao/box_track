from django.urls import path
from django.views.generic import TemplateView

from .views import USCompareView

urlpatterns = [
    path('', TemplateView.as_view(template_name='frontend/box.html'), name='box'),
    path('us_cmp', USCompareView.as_view(), name='us_cmp'),
]
