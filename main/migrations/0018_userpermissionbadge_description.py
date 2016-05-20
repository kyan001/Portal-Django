# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0017_auto_20160519_1727'),
    ]

    operations = [
        migrations.AddField(
            model_name='userpermissionbadge',
            name='description',
            field=models.TextField(default=''),
        ),
    ]
