# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0019_auto_20160520_1441'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userpermissionbadge',
            name='image',
            field=models.TextField(default='/static/media/badges/no.png'),
        ),
    ]
