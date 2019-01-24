# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='InitialItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('europeana_id', models.CharField(max_length=250)),
                ('title', models.CharField(max_length=250)),
                ('description', models.TextField()),
                ('resource_type', models.CharField(max_length=20)),
                ('thumbnail', models.URLField()),
                ('url', models.URLField()),
            ],
        ),
    ]
