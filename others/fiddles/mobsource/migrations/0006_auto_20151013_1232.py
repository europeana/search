# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mobsource', '0005_auto_20151013_1014'),
    ]

    operations = [
        migrations.AlterField(
            model_name='language',
            name='id',
            field=models.AutoField(serialize=False, primary_key=True),
        ),
    ]
