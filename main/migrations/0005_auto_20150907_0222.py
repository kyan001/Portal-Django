# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_opus_progress'),
    ]

    operations = [
        migrations.AlterField(
            model_name='opus',
            name='name',
            field=models.CharField(max_length=255),
        ),
    ]
