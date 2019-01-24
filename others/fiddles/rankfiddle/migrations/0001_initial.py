# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CandidateBoostFields',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('field_name', models.CharField(verbose_name='field name', max_length=50, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Query',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('query_text', models.CharField(verbose_name='query text', max_length=255, unique=True)),
            ],
            options={
                'verbose_name_plural': 'query',
            },
        ),
    ]
