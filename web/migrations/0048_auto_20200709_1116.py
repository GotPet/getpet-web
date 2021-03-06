# Generated by Django 3.0.7 on 2020-07-09 11:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0047_auto_20200709_1051'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='shelter',
            options={'default_related_name': 'shelters', 'ordering': ('order', 'id'), 'verbose_name': 'Gyvūnų prieglauda', 'verbose_name_plural': 'Gyvūnų prieglaudos'},
        ),
        migrations.AddField(
            model_name='shelter',
            name='order',
            field=models.IntegerField(default=0, editable=False),
        ),
        migrations.AlterIndexTogether(
            name='shelter',
            index_together={('order', 'id')},
        ),
    ]
