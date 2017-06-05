# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mobsource', '0012_auto_20151023_1508'),
    ]

    operations = [
        migrations.AddField(
            model_name='queryresult',
            name='timestamp',
            field=models.DateTimeField(null=True, auto_now_add=True),
        ),
    ]
