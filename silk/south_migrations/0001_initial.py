# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Request'
        db.create_table('silk_request', (
            ('id', self.gf('django.db.models.fields.CharField')(primary_key=True, max_length=36)),
            ('path', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=300)),
            ('query_params', self.gf('django.db.models.fields.TextField')(blank=True, default='')),
            ('raw_body', self.gf('django.db.models.fields.TextField')(blank=True, default='')),
            ('body', self.gf('django.db.models.fields.TextField')(blank=True, default='')),
            ('method', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')(db_index=True, default=datetime.datetime.now)),
            ('view_name', self.gf('django.db.models.fields.CharField')(db_index=True, blank=True, default='', max_length=300, null=True)),
            ('end_time', self.gf('django.db.models.fields.DateTimeField')(blank=True, null=True)),
            ('time_taken', self.gf('django.db.models.fields.FloatField')(blank=True, null=True)),
            ('encoded_headers', self.gf('django.db.models.fields.TextField')(blank=True, default='')),
            ('meta_time', self.gf('django.db.models.fields.FloatField')(blank=True, null=True)),
            ('meta_num_queries', self.gf('django.db.models.fields.IntegerField')(blank=True, null=True)),
            ('meta_time_spent_queries', self.gf('django.db.models.fields.FloatField')(blank=True, null=True)),
            ('pyprofile', self.gf('django.db.models.fields.TextField')(blank=True, default='')),
            ('num_sql_queries', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('silk', ['Request'])

        # Adding model 'Response'
        db.create_table('silk_response', (
            ('id', self.gf('django.db.models.fields.CharField')(primary_key=True, max_length=36)),
            ('request', self.gf('django.db.models.fields.related.OneToOneField')(related_name='response', to=orm['silk.Request'], unique=True)),
            ('status_code', self.gf('django.db.models.fields.IntegerField')()),
            ('raw_body', self.gf('django.db.models.fields.TextField')(blank=True, default='')),
            ('body', self.gf('django.db.models.fields.TextField')(blank=True, default='')),
            ('encoded_headers', self.gf('django.db.models.fields.TextField')(blank=True, default='')),
        ))
        db.send_create_signal('silk', ['Response'])

        # Adding model 'SQLQuery'
        db.create_table('silk_sqlquery', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('query', self.gf('django.db.models.fields.TextField')()),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')(blank=True, null=True, default=datetime.datetime.now)),
            ('end_time', self.gf('django.db.models.fields.DateTimeField')(blank=True, null=True)),
            ('time_taken', self.gf('django.db.models.fields.FloatField')(blank=True, null=True)),
            ('request', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='queries', null=True, to=orm['silk.Request'])),
            ('traceback', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('silk', ['SQLQuery'])

        # Adding model 'Profile'
        db.create_table('silk_profile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(blank=True, default='', max_length=300)),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('end_time', self.gf('django.db.models.fields.DateTimeField')(blank=True, null=True)),
            ('request', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, null=True, to=orm['silk.Request'])),
            ('time_taken', self.gf('django.db.models.fields.FloatField')(blank=True, null=True)),
            ('file_path', self.gf('django.db.models.fields.CharField')(blank=True, default='', max_length=300)),
            ('line_num', self.gf('django.db.models.fields.IntegerField')(blank=True, null=True)),
            ('end_line_num', self.gf('django.db.models.fields.IntegerField')(blank=True, null=True)),
            ('func_name', self.gf('django.db.models.fields.CharField')(blank=True, default='', max_length=300)),
            ('exception_raised', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('dynamic', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('silk', ['Profile'])

        # Adding M2M table for field queries on 'Profile'
        m2m_table_name = db.shorten_name('silk_profile_queries')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('profile', models.ForeignKey(orm['silk.profile'], null=False)),
            ('sqlquery', models.ForeignKey(orm['silk.sqlquery'], null=False))
        ))
        db.create_unique(m2m_table_name, ['profile_id', 'sqlquery_id'])


    def backwards(self, orm):
        # Deleting model 'Request'
        db.delete_table('silk_request')

        # Deleting model 'Response'
        db.delete_table('silk_response')

        # Deleting model 'SQLQuery'
        db.delete_table('silk_sqlquery')

        # Deleting model 'Profile'
        db.delete_table('silk_profile')

        # Removing M2M table for field queries on 'Profile'
        db.delete_table(db.shorten_name('silk_profile_queries'))


    models = {
        'silk.profile': {
            'Meta': {'object_name': 'Profile'},
            'dynamic': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'end_line_num': ('django.db.models.fields.IntegerField', [], {'blank': 'True', 'null': 'True'}),
            'end_time': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'null': 'True'}),
            'exception_raised': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'file_path': ('django.db.models.fields.CharField', [], {'blank': 'True', 'default': "''", 'max_length': '300'}),
            'func_name': ('django.db.models.fields.CharField', [], {'blank': 'True', 'default': "''", 'max_length': '300'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'line_num': ('django.db.models.fields.IntegerField', [], {'blank': 'True', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'blank': 'True', 'default': "''", 'max_length': '300'}),
            'queries': ('django.db.models.fields.related.ManyToManyField', [], {'db_index': 'True', 'related_name': "'profiles'", 'symmetrical': 'False', 'to': "orm['silk.SQLQuery']"}),
            'request': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'null': 'True', 'to': "orm['silk.Request']"}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'time_taken': ('django.db.models.fields.FloatField', [], {'blank': 'True', 'null': 'True'})
        },
        'silk.request': {
            'Meta': {'object_name': 'Request'},
            'body': ('django.db.models.fields.TextField', [], {'blank': 'True', 'default': "''"}),
            'encoded_headers': ('django.db.models.fields.TextField', [], {'blank': 'True', 'default': "''"}),
            'end_time': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'null': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'primary_key': 'True', 'max_length': '36'}),
            'meta_num_queries': ('django.db.models.fields.IntegerField', [], {'blank': 'True', 'null': 'True'}),
            'meta_time': ('django.db.models.fields.FloatField', [], {'blank': 'True', 'null': 'True'}),
            'meta_time_spent_queries': ('django.db.models.fields.FloatField', [], {'blank': 'True', 'null': 'True'}),
            'method': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'num_sql_queries': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'path': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '300'}),
            'pyprofile': ('django.db.models.fields.TextField', [], {'blank': 'True', 'default': "''"}),
            'query_params': ('django.db.models.fields.TextField', [], {'blank': 'True', 'default': "''"}),
            'raw_body': ('django.db.models.fields.TextField', [], {'blank': 'True', 'default': "''"}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'default': 'datetime.datetime.now'}),
            'time_taken': ('django.db.models.fields.FloatField', [], {'blank': 'True', 'null': 'True'}),
            'view_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'blank': 'True', 'default': "''", 'max_length': '300', 'null': 'True'})
        },
        'silk.response': {
            'Meta': {'object_name': 'Response'},
            'body': ('django.db.models.fields.TextField', [], {'blank': 'True', 'default': "''"}),
            'encoded_headers': ('django.db.models.fields.TextField', [], {'blank': 'True', 'default': "''"}),
            'id': ('django.db.models.fields.CharField', [], {'primary_key': 'True', 'max_length': '36'}),
            'raw_body': ('django.db.models.fields.TextField', [], {'blank': 'True', 'default': "''"}),
            'request': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'response'", 'to': "orm['silk.Request']", 'unique': 'True'}),
            'status_code': ('django.db.models.fields.IntegerField', [], {})
        },
        'silk.sqlquery': {
            'Meta': {'object_name': 'SQLQuery'},
            'end_time': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'query': ('django.db.models.fields.TextField', [], {}),
            'request': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'queries'", 'null': 'True', 'to': "orm['silk.Request']"}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'null': 'True', 'default': 'datetime.datetime.now'}),
            'time_taken': ('django.db.models.fields.FloatField', [], {'blank': 'True', 'null': 'True'}),
            'traceback': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['silk']
