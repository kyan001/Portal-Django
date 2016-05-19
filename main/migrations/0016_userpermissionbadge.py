# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0015_userpermission'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserPermissionBadge',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('category', models.CharField(max_length=128)),
                ('isallowd', models.BooleanField()),
                ('image', models.ImageField(default='default.jpg', upload_to='badges')),
            ],
        ),
    ]
