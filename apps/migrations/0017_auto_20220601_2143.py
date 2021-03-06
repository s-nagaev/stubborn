# Generated by Django 3.2.13 on 2022-06-01 21:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0016_requestlog_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='resourcestub',
            name='response_type',
            field=models.CharField(choices=[(0, 'Custom Response'), (1, 'Proxy Specific URL'), (2, 'Global Proxy')], default=0, max_length=30),
        ),
        migrations.AlterField(
            model_name='responsestub',
            name='format',
            field=models.CharField(choices=[('JSON', 'JSON'), ('XML', 'XML'), ('PLAIN_TEXT', 'Text')], default='PLAIN_TEXT', max_length=10, verbose_name='Format'),
        ),
    ]
