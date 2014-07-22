# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Blind'
        db.create_table(u'example_app_blind', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('photo', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('name', self.gf('django.db.models.fields.TextField')()),
            ('child_safe', self.gf('django.db.models.fields.BooleanField')()),
        ))
        db.send_create_signal(u'example_app', ['Blind'])


    def backwards(self, orm):
        # Deleting model 'Blind'
        db.delete_table(u'example_app_blind')


    models = {
        u'example_app.blind': {
            'Meta': {'object_name': 'Blind'},
            'child_safe': ('django.db.models.fields.BooleanField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {}),
            'photo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['example_app']