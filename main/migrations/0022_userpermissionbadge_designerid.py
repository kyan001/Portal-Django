# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0021_auto_20160520_1557'),
    ]

    operations = [
        migrations.AddField(
            model_name='userpermissionbadge',
            name='designerid',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
