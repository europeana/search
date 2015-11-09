# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mobsource', '0008_remove_email_query'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='query',
            options={'verbose_name_plural': 'queries'},
        ),
        migrations.AlterField(
            model_name='language',
            name='language_code',
            field=models.CharField(max_length=3),
        ),
    ]
