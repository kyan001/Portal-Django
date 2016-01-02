# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0011_auto_20151130_1727'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExpHistory',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('userexpid', models.IntegerField(default=0)),
                ('operation', models.TextField()),
                ('change', models.IntegerField(default=0)),
                ('created', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='UserExp',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('userid', models.IntegerField(default=0)),
                ('category', models.CharField(max_length=255)),
                ('exp', models.IntegerField(default=0)),
                ('modified', models.DateTimeField()),
                ('created', models.DateTimeField()),
            ],
        ),
    ]
