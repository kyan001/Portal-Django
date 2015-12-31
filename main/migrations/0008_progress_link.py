# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_remove_opus_tags'),
    ]

    operations = [
        migrations.AddField(
            model_name='progress',
            name='link',
            field=models.URLField(blank=True, null=True, max_length=2083),
        ),
    ]
