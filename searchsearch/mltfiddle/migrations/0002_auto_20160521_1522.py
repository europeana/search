# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mltfiddle', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='initialitem',
            name='title',
            field=models.CharField(max_length=500),
        ),
    ]
