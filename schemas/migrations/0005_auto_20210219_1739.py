# Generated by Django 3.1.6 on 2021-02-19 20:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schemas', '0004_attribute__value'),
    ]

    operations = [
        migrations.RenameField(
            model_name='attribute',
            old_name='_value',
            new_name='attr_value',
        ),
    ]
