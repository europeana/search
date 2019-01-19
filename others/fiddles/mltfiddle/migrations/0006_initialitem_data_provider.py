# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mltfiddle', '0005_auto_20160608_0835'),
    ]

    operations = [
        migrations.AddField(
            model_name='initialitem',
            name='data_provider',
            field=models.CharField(max_length=150, default='rj'),
        ),
    ]
