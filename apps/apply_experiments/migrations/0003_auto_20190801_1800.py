# Generated by Django 2.1 on 2019-08-01 10:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apply_experiments', '0002_auto_20190721_2059'),
    ]

    operations = [
        migrations.RenameField(
            model_name='experiment',
            old_name='lesson',
            new_name='course',
        ),
    ]