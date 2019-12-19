# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mltfiddle', '0003_auto_20160521_1524'),
    ]

    operations = [
        migrations.CreateModel(
            name='FieldName',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('field_name', models.CharField(max_length=75)),
            ],
        ),
    ]
