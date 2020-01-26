from django.urls import path

from .views import GetJapanBox, UpdateBoxApi, DumpDataApi, AnimatedBoxOffice, Top10Movie, USCompareView

urlpatterns = [
    path('japan_box', GetJapanBox.as_view(), name='get_japan_box'),
    path('update', UpdateBoxApi.as_view(), name='update_box'),
    path('dump', DumpDataApi.as_view(), name='dump_data'),
    path('animatedbox', AnimatedBoxOffice.as_view(), name='animatedbox'),
    path('top10', Top10Movie.as_view(), name='top10'),
    path('us_cmp', USCompareView.as_view(), name='us_cmp'),
]
