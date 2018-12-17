# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-02-26 16:38
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('awards', '0024_auto_20180222_1504'),
    ]

    operations = [
        # This is already handled by index defined on awards table in usaspending_api/awards/models.py
        # Keeping this was causing an error when migrating from scratch.
        # migrations.RunSQL(sql="CREATE INDEX awards_update_date_desc_idx ON awards (update_date DESC)",
        #                   reverse_sql="DROP INDEX awards_update_date_desc_idx")
    ]
