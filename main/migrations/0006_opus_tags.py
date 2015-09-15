# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_auto_20150907_0222'),
    ]

    operations = [
        migrations.AddField(
            model_name='opus',
            name='tags',
            field=models.CharField(null=True, default='', max_length=255, blank=True),
        ),
    ]
