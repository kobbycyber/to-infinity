# Generated by Django 3.1.4 on 2020-12-08 14:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0008_delete_trip'),
    ]

    operations = [
        migrations.AddField(
            model_name='destination',
            name='addons',
            field=models.ManyToManyField(to='products.AddOn'),
        ),
    ]