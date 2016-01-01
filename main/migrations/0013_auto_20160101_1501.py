# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_exphistory_userexp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exphistory',
            name='created',
            field=models.DateTimeField(default=django.utils.timezone.now, blank=True),
        ),
        migrations.AlterField(
            model_name='opus',
            name='created',
            field=models.DateTimeField(default=django.utils.timezone.now, blank=True),
        ),
        migrations.AlterField(
            model_name='progress',
            name='created',
            field=models.DateTimeField(default=django.utils.timezone.now, blank=True),
        ),
        migrations.AlterField(
            model_name='progress',
            name='modified',
            field=models.DateTimeField(default=django.utils.timezone.now, blank=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='created',
            field=models.DateTimeField(default=django.utils.timezone.now, blank=True),
        ),
        migrations.AlterField(
            model_name='userexp',
            name='created',
            field=models.DateTimeField(default=django.utils.timezone.now, blank=True),
        ),
        migrations.AlterField(
            model_name='userexp',
            name='modified',
            field=models.DateTimeField(default=django.utils.timezone.now, blank=True),
        ),
    ]
