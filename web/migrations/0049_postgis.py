from django.contrib.postgres.operations import CreateExtension
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('web', '0048_auto_20200709_1116'),
    ]

    operations = [
        CreateExtension('postgis'),
    ]
