# Generated by Django 3.0.4 on 2020-04-30 23:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0011_auto_20200430_2256'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pet',
            name='age',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Amžius'),
        ),
        migrations.AlterField(
            model_name='pet',
            name='weight',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Svoris'),
        ),
    ]
