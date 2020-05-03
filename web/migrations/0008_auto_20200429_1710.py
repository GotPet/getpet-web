# Generated by Django 3.0.4 on 2020-04-29 17:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0007_auto_20200428_1927'),
    ]

    operations = [
        migrations.AddField(
            model_name='shelter',
            name='address',
            field=models.CharField(max_length=256, null=True, verbose_name='Adresas'),
        ),
        migrations.AddField(
            model_name='shelter',
            name='facebook',
            field=models.URLField(blank=True, null=True, verbose_name='Facebook'),
        ),
        migrations.AddField(
            model_name='shelter',
            name='instagram',
            field=models.URLField(blank=True, null=True, verbose_name='Instagram'),
        ),
        migrations.AddField(
            model_name='shelter',
            name='is_published',
            field=models.BooleanField(db_index=True, default=True, help_text='Pažymėjus prieglauda matoma viešai', verbose_name='Paskelbta'),
        ),
        migrations.AddField(
            model_name='shelter',
            name='legal_name',
            field=models.CharField(max_length=256, null=True, verbose_name='Prieglaudos pavadinimas'),
        ),
        migrations.AddField(
            model_name='shelter',
            name='website',
            field=models.URLField(blank=True, null=True, verbose_name='Interneto svetainė'),
        ),
    ]