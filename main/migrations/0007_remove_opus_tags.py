# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_opus_tags'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='opus',
            name='tags',
        ),
    ]
