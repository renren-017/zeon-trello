# Generated by Django 4.1.3 on 2022-11-23 13:19

import colorfield.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('boards', '0004_alter_cardlabel_color'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cardlabel',
            name='color',
            field=colorfield.fields.ColorField(default='#000', image_field=None, max_length=18, samples=None),
        ),
    ]
