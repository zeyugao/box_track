# Generated by Django 3.0.1 on 2019-12-27 06:37

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='JapanBox',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('update_time', models.DateTimeField()),
                ('frozen_box', models.TextField()),
                ('full_info', models.TextField()),
            ],
        ),
    ]
