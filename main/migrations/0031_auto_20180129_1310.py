# Generated by Django 2.0.1 on 2018-01-29 05:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0030_auto_20171031_1842'),
    ]

    operations = [
        migrations.RenameField(
            model_name='opus',
            old_name='subtitle',
            new_name='comment',
        ),
    ]
