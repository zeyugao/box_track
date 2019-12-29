from django.db import models

# Create your models here.


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


class JapanBoxFull(models.Model):
    full_info = models.TextField()
    update_time = models.DateTimeField()

    store_time = models.DateTimeField()
