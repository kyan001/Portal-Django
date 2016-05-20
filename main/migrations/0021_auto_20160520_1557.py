# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0020_auto_20160520_1448'),
    ]

    operations = [
        migrations.AddField(
            model_name='userpermissionbadge',
            name='created',
            field=models.DateTimeField(default=django.utils.timezone.now, blank=True),
        ),
        migrations.AddField(
            model_name='userpermissionbadge',
            name='requirement',
            field=models.TextField(default=''),
        ),
    ]
