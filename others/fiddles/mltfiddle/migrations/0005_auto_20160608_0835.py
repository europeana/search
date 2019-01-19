# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mltfiddle', '0004_fieldname'),
    ]

    operations = [
        migrations.AddField(
            model_name='initialitem',
            name='original_page',
            field=models.URLField(max_length=350, default='www.example.com'),
        ),
        migrations.AlterField(
            model_name='initialitem',
            name='url',
            field=models.URLField(max_length=250),
        ),
    ]
