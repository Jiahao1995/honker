# Generated by Django 3.1.3 on 2021-08-25 01:53

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('honks', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='honk',
            options={'ordering': ('user', '-created_at')},
        ),
        migrations.AlterIndexTogether(
            name='honk',
            index_together={('user', 'created_at')},
        ),
    ]
