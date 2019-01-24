# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('mobsource', '0011_delete_email'),
    ]

    operations = [
        migrations.CreateModel(
            name='QueryResult',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('europeana_id', models.CharField(max_length=100)),
                ('position', models.PositiveSmallIntegerField(validators=[django.core.validators.MaxValueValidator(10)])),
                ('rating', models.PositiveSmallIntegerField(validators=[django.core.validators.MaxValueValidator(5)])),
            ],
        ),
        migrations.AddField(
            model_name='query',
            name='ndcg',
            field=models.DecimalField(max_digits=4, decimal_places=3, null=True),
        ),
        migrations.AddField(
            model_name='queryresult',
            name='query',
            field=models.ForeignKey(to='mobsource.Query', related_name='response_to'),
        ),
    ]
