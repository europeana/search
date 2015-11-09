# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mobsource', '0007_auto_20151013_1234'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='email',
            name='query',
        ),
    ]
