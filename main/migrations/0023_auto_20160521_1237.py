# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0022_userpermissionbadge_designerid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userpermissionbadge',
            name='designerid',
        ),
        migrations.AddField(
            model_name='userpermissionbadge',
            name='designernname',
            field=models.CharField(max_length=128, null=True, blank=True, default=''),
        ),
    ]
