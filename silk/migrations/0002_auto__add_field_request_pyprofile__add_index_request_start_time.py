# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Request.pyprofile'
        db.add_column(u'silk_request', 'pyprofile',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding index on 'Request', fields ['start_time']
        db.create_index(u'silk_request', ['start_time'])


    def backwards(self, orm):
        # Removing index on 'Request', fields ['start_time']
        db.delete_index(u'silk_request', ['start_time'])

        # Deleting field 'Request.pyprofile'
        db.delete_column(u'silk_request', 'pyprofile')


    models = {
        u'silk.profile': {
            'Meta': {'object_name': 'Profile'},
            'dynamic': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'end_line_num': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'end_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'exception_raised': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'file_path': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '300', 'blank': 'True'}),
            'func_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '300', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'line_num': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '300', 'blank': 'True'}),
            'queries': ('django.db.models.fields.related.ManyToManyField', [], {'db_index': 'True', 'related_name': "'profiles'", 'symmetrical': 'False', 'to': u"orm['silk.SQLQuery']"}),
            'request': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['silk.Request']", 'null': 'True', 'blank': 'True'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'time_taken': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        u'silk.request': {
            'Meta': {'object_name': 'Request'},
            'body': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'encoded_headers': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'end_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'meta_num_queries': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'meta_time': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'meta_time_spent_queries': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'method': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'num_sql_queries': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '300', 'db_index': 'True'}),
            'pyprofile': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'query_params': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'raw_body': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'db_index': 'True'}),
            'time_taken': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'view_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '300', 'db_index': 'True', 'blank': 'True'})
        },
        u'silk.response': {
            'Meta': {'object_name': 'Response'},
            'body': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'encoded_headers': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'raw_body': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'request': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'response'", 'unique': 'True', 'to': u"orm['silk.Request']"}),
            'status_code': ('django.db.models.fields.IntegerField', [], {})
        },
        u'silk.sqlquery': {
            'Meta': {'object_name': 'SQLQuery'},
            'end_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'query': ('django.db.models.fields.TextField', [], {}),
            'request': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'queries'", 'null': 'True', 'to': u"orm['silk.Request']"}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'null': 'True', 'blank': 'True'}),
            'time_taken': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'traceback': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['silk']