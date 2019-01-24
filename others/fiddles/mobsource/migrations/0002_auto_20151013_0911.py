# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mobsource', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='query',
            name='language',
            field=models.ForeignKey(related_name='target_language', to='mobsource.Language'),
        ),
        migrations.AlterField(
            model_name='query',
            name='source',
            field=models.ForeignKey(related_name='query_by', to='mobsource.Email'),
        ),
    ]
