from django.db import models

# Create your models here.

class JapanBox(models.Model):
    update_time = models.DateTimeField()
    frozen_box = models.TextField()

    full_info = models.TextField()