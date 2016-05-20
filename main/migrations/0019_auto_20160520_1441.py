# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0018_userpermissionbadge_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userpermissionbadge',
            name='image',
            field=models.URLField(max_length=100, default='/static/media/badges/no.png'),
        ),
    ]
