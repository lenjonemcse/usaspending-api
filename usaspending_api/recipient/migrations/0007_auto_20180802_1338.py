# -*- coding: utf-8 -*-
# Generated by Django 1.11.14 on 2018-08-02 13:38
from __future__ import unicode_literals

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipient', '0006_auto_20180727_1940'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipientprofile',
            name='last_12_months_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='duns',
            name='business_types_codes',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.TextField(), default=list, null=True, size=None),
        ),
        migrations.AlterField(
            model_name='recipientprofile',
            name='recipient_hash',
            field=models.UUIDField(db_index=True, null=True),
        ),
        migrations.AlterField(
            model_name='recipientprofile',
            name='recipient_name',
            field=models.TextField(db_index=True, null=True),
        ),
        migrations.AlterField(
            model_name='recipientprofile',
            name='recipient_unique_id',
            field=models.TextField(db_index=True, null=True),
        ),
    ]
