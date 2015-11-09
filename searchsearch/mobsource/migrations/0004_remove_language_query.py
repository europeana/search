# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mobsource', '0003_auto_20151013_0915'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='language',
            name='query',
        ),
    ]
