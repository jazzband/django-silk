from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('silk', '0008_sqlquery_analysis'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='sqlquery',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]