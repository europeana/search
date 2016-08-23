# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Agent',
            fields=[
                ('wdid', models.URLField(primary_key=True, serialize=False, unique=True)),
                ('pref_label', models.CharField(max_length=500)),
                ('sex', models.CharField(max_length=7, choices=[('male', 'Male'), ('female', 'Female'), ('unknown', 'Unknown')])),
                ('place_of_birth', models.CharField(max_length=500)),
                ('place_of_death', models.CharField(max_length=500)),
                ('europeana_narrow_set', models.URLField()),
                ('europeana_broad_set', models.URLField()),
            ],
        ),
        migrations.CreateModel(
            name='AgentImage',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('image_url', models.URLField(max_length=401)),
                ('agent', models.OneToOneField(to='jansixdegrees.Agent', related_name='portrait', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='AgentRole',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('pref_label', models.CharField(max_length=100)),
                ('agent', models.ForeignKey(to='jansixdegrees.Agent')),
            ],
        ),
        migrations.CreateModel(
            name='EuropeanaWork',
            fields=[
                ('euid', models.URLField(primary_key=True, serialize=False, unique=True)),
                ('pref_label', models.CharField(max_length=250)),
                ('creator', models.ManyToManyField(related_name='eu_work_creator', to='jansixdegrees.Agent')),
                ('subject', models.ManyToManyField(related_name='eu_work_subject', to='jansixdegrees.Agent')),
            ],
        ),
        migrations.CreateModel(
            name='RelationshipType',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('pref_label', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='SocialRelation',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('active', models.ForeignKey(to='jansixdegrees.Agent', related_name='originator')),
                ('passive', models.ForeignKey(to='jansixdegrees.Agent', related_name='recipient')),
                ('relationship_type', models.ForeignKey(to='jansixdegrees.RelationshipType', related_name='rtype')),
            ],
        ),
        migrations.CreateModel(
            name='Work',
            fields=[
                ('wdid', models.URLField(primary_key=True, serialize=False, unique=True)),
                ('pref_label', models.CharField(max_length=250)),
                ('creator', models.ManyToManyField(related_name='work_creator', to='jansixdegrees.Agent')),
                ('subject', models.ManyToManyField(related_name='work_subject', to='jansixdegrees.Agent')),
            ],
        ),
        migrations.AddField(
            model_name='agent',
            name='social_relation',
            field=models.ManyToManyField(through='jansixdegrees.SocialRelation', to='jansixdegrees.Agent'),
        ),
    ]
