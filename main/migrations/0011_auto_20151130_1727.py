# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_auto_20151130_1726'),
    ]

    operations = [
        migrations.AlterField(
            model_name='progress',
            name='weblink',
            field=models.URLField(blank=True, max_length=2083, default=''),
        ),
    ]
