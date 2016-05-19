# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0016_userpermissionbadge'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userpermissionbadge',
            old_name='isallowd',
            new_name='isallowed',
        ),
    ]
