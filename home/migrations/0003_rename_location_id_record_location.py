# Generated by Django 3.2.4 on 2021-06-26 15:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0002_auto_20210626_1525'),
    ]

    operations = [
        migrations.RenameField(
            model_name='record',
            old_name='location_id',
            new_name='location',
        ),
    ]