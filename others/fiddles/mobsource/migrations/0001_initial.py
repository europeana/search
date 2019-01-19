# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Email',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('address', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('language', models.CharField(max_length=2, choices=[('en', 'English'), ('fr', 'French')])),
            ],
        ),
        migrations.CreateModel(
            name='Query',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('query_text', models.CharField(verbose_name='query text', max_length=255)),
                ('language', models.OneToOneField(to='mobsource.Language', related_name='target_language')),
                ('source', models.OneToOneField(to='mobsource.Email', related_name='query_by')),
            ],
        ),
        migrations.CreateModel(
            name='QueryComment',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('comment_text', models.TextField(blank=True)),
                ('query', models.OneToOneField(to='mobsource.Query')),
            ],
        ),
        migrations.CreateModel(
            name='QueryMotive',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('motive_text', models.TextField(blank=True)),
                ('query', models.OneToOneField(to='mobsource.Query')),
            ],
        ),
        migrations.AddField(
            model_name='language',
            name='query',
            field=models.ForeignKey(related_name='query_lang', to='mobsource.Query'),
        ),
        migrations.AddField(
            model_name='email',
            name='query',
            field=models.ForeignKey(related_name='query_creator', to='mobsource.Query'),
        ),
    ]
