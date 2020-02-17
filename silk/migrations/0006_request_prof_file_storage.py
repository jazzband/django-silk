# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import silk.storage


class Migration(migrations.Migration):

    dependencies = [
        ('silk', '0005_increase_request_prof_file_length'),
    ]

    operations = [
        migrations.AlterField(
            model_name='request',
            name='prof_file',
            field=models.FileField(default='', storage=silk.storage.ProfilerResultStorage(), max_length=300,
                                   upload_to=b'', blank=True),
            preserve_default=False,
        ),
    ]
