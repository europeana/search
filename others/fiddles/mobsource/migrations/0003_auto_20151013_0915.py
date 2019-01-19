# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mobsource', '0002_auto_20151013_0911'),
    ]

    operations = [
        migrations.AlterField(
            model_name='query',
            name='query_text',
            field=models.CharField(max_length=255, verbose_name='query text', unique=True),
        ),
    ]
