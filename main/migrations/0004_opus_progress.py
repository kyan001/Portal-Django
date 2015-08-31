# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_user_nickname'),
    ]

    operations = [
        migrations.CreateModel(
            name='Opus',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=255, unique=True)),
                ('subtitle', models.CharField(null=True, max_length=255, blank=True)),
                ('total', models.IntegerField(default=0)),
                ('created', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Progress',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('userid', models.IntegerField(default=0)),
                ('opusid', models.IntegerField(default=0)),
                ('current', models.IntegerField(default=0)),
                ('status', models.CharField(max_length=50)),
                ('created', models.DateTimeField()),
                ('modified', models.DateTimeField()),
            ],
        ),
    ]
