# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-25 05:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='pool',
            name='max_size',
            field=models.PositiveSmallIntegerField(default=5),
        ),
    ]
