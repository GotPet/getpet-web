# Generated by Django 3.0.6 on 2020-05-07 18:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0018_auto_20200507_1820'),
    ]

    operations = [
        migrations.AddField(
            model_name='pet',
            name='taken_at',
            field=models.DateTimeField(blank=True, editable=False, null=True, verbose_name='Paėmimo data'),
        ),
    ]
