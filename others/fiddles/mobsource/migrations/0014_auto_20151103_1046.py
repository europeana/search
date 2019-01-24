# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mobsource', '0013_queryresult_timestamp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='queryresult',
            name='europeana_id',
            field=models.CharField(max_length=255),
        ),
    ]
