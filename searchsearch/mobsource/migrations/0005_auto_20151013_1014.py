# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mobsource', '0004_remove_language_query'),
    ]

    operations = [
        migrations.AddField(
            model_name='language',
            name='language_code',
            field=models.CharField(max_length=2, default='en'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='language',
            name='language',
            field=models.CharField(max_length=30),
        ),
    ]
