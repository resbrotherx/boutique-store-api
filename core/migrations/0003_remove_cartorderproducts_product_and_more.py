# Generated by Django 4.2.8 on 2024-02-04 09:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_cartorderproducts_product'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cartorderproducts',
            name='product',
        ),
        migrations.RemoveField(
            model_name='cartorderproducts',
            name='user',
        ),
    ]
