# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-09-08 21:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vosi', '0002_remove_availability_enabled'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='availability',
            name='available',
        ),
        migrations.RemoveField(
            model_name='availability',
            name='note',
        ),
        migrations.AlterField(
            model_name='availability',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
