# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mobsource', '0010_auto_20151015_1621'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Email',
        ),
    ]
