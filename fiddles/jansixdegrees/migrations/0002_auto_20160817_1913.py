# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jansixdegrees', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='agent',
            name='birthdate',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='agent',
            name='deathdate',
            field=models.CharField(max_length=20, null=True),
        ),
    ]
