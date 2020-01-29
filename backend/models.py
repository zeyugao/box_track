from django.db import models

# Create your models here.

'''
class JapanBox(models.Model):
    update_time = models.DateTimeField()
    rank = models.IntegerField()
    sale = models.IntegerField()
    sale_inc = models.IntegerField()
    seat = models.IntegerField()
    seat_used = models.FloatField()
    rate_last_week = models.FloatField()
    rate_95 = models.FloatField()
    estimation = models.IntegerField()
    name = models.CharField(max_length=127)
'''


class JapanBoxFull(models.Model):
    full_info = models.TextField()
    update_time = models.DateTimeField()

    store_time = models.DateTimeField()


'''
class Maoyan(models.Model):
    update_time = models.DateTimeField()
    avgSeatView = models.FloatField()  # 上座率
    avgShowView = models.IntegerField()  # 场均人次
    avgViewBox = models.FloatField()  # 平均票价
    boxInfo = models.FloatField()  # 综合票房
    boxRate = models.FloatField()  # 票房占比
    movieId = models.IntegerField()
    movieName = models.CharField(max_length=255)
    seatRate = models.FloatField()  # 排座占比
    showInfo = models.IntegerField()  # 拍片场次
    showRate = models.FloatField()  # 排片占比
    sumBoxInfo = models.CharField(max_length=31)  # 总票房
    viewInfo = models.FloatField()  # 人次
    viewInfoV2 = models.CharField(max_length=31)
'''


class MaoyanFull(models.Model):
    update_time = models.DateTimeField()

    full_info = models.TextField()


class BoxOfficeMojoDomestic(models.Model):
    movie_name = models.CharField(max_length=127)
    day = models.IntegerField()
    daily = models.IntegerField()
    DOW = models.IntegerField()
    date = models.DateField()
    to_date = models.IntegerField()
