# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-12 06:36
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('provapp', '0007_ecollection'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hadmember',
            name='collection',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='provapp.ECollection'),
        ),
    ]
