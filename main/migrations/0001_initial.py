# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('username', models.CharField(unique=True, max_length=255)),
                ('question', models.TextField()),
                ('answer1', models.CharField(max_length=128)),
                ('answer2', models.CharField(blank=True, null=True, max_length=128)),
                ('tip', models.TextField(blank=True, null=True)),
                ('email', models.EmailField(max_length=254)),
                ('created', models.DateTimeField(default=datetime.datetime(2015, 8, 8, 9, 25, 24, 66902, tzinfo=utc))),
            ],
        ),
    ]
