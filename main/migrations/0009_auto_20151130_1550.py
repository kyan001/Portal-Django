# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_progress_link'),
    ]

    operations = [
        migrations.RenameField(
            model_name='progress',
            old_name='link',
            new_name='weblink',
        ),
    ]
