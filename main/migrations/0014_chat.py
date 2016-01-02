# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0013_auto_20160101_1501'),
    ]

    operations = [
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('senderid', models.IntegerField(default=0)),
                ('receiverid', models.IntegerField(default=0)),
                ('title', models.TextField(null=True, blank=True)),
                ('content', models.TextField(null=True, blank=True)),
                ('isread', models.BooleanField(default=False)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
    ]
