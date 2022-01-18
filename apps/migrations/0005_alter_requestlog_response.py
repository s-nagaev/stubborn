# Generated by Django 3.2.9 on 2021-11-24 08:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0004_alter_resourcestub_unique_together'),
    ]

    operations = [
        migrations.AlterField(
            model_name='requestlog',
            name='response',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='logs', to='apps.responsestub', verbose_name='Response'),
        ),
    ]