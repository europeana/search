# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mltfiddle', '0002_auto_20160521_1522'),
    ]

    operations = [
        migrations.AlterField(
            model_name='initialitem',
            name='thumbnail',
            field=models.URLField(max_length=350),
        ),
    ]
