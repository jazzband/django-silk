# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Request'
        db.create_table(u'silk_request', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('path', self.gf('django.db.models.fields.CharField')(max_length=300, db_index=True)),
            ('query_params', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('raw_body', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('body', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('method', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('view_name', self.gf('django.db.models.fields.CharField')(default='', max_length=300, db_index=True, blank=True)),
            ('end_time', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('time_taken', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('encoded_headers', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('meta_time', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('meta_num_queries', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('meta_time_spent_queries', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('num_sql_queries', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'silk', ['Request'])

        # Adding model 'Response'
        db.create_table(u'silk_response', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('request', self.gf('django.db.models.fields.related.OneToOneField')(related_name='response', unique=True, to=orm['silk.Request'])),
            ('status_code', self.gf('django.db.models.fields.IntegerField')()),
            ('raw_body', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('body', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('encoded_headers', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
        ))
        db.send_create_signal(u'silk', ['Response'])

        # Adding model 'SQLQuery'
        db.create_table(u'silk_sqlquery', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('query', self.gf('django.db.models.fields.TextField')()),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, null=True, blank=True)),
            ('end_time', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('time_taken', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('request', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='queries', null=True, to=orm['silk.Request'])),
            ('traceback', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'silk', ['SQLQuery'])

        # Adding model 'Profile'
        db.create_table(u'silk_profile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(default='', max_length=300, blank=True)),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('end_time', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('request', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['silk.Request'], null=True, blank=True)),
            ('time_taken', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('file_path', self.gf('django.db.models.fields.CharField')(default='', max_length=300, blank=True)),
            ('line_num', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('end_line_num', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('func_name', self.gf('django.db.models.fields.CharField')(default='', max_length=300, blank=True)),
            ('exception_raised', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('dynamic', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'silk', ['Profile'])

        # Adding M2M table for field queries on 'Profile'
        m2m_table_name = db.shorten_name(u'silk_profile_queries')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('profile', models.ForeignKey(orm[u'silk.profile'], null=False)),
            ('sqlquery', models.ForeignKey(orm[u'silk.sqlquery'], null=False))
        ))
        db.create_unique(m2m_table_name, ['profile_id', 'sqlquery_id'])


    def backwards(self, orm):
        # Deleting model 'Request'
        db.delete_table(u'silk_request')

        # Deleting model 'Response'
        db.delete_table(u'silk_response')

        # Deleting model 'SQLQuery'
        db.delete_table(u'silk_sqlquery')

        # Deleting model 'Profile'
        db.delete_table(u'silk_profile')

        # Removing M2M table for field queries on 'Profile'
        db.delete_table(db.shorten_name(u'silk_profile_queries'))


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
            'queries': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'profiles'", 'symmetrical': 'False', 'to': u"orm['silk.SQLQuery']"}),
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
            'query_params': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'raw_body': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
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