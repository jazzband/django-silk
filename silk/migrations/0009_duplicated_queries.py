# Generated by Django 3.2.16 on 2022-10-25 17:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('silk', '0008_sqlquery_analysis'),
    ]

    operations = [
        migrations.AddField(
            model_name='request',
            name='num_duplicated_queries',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='sqlquery',
            name='query_structure',
            field=models.TextField(default=''),
        ),
    ]
