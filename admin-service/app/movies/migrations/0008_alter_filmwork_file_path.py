# Generated by Django 3.2 on 2023-09-30 14:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0007_auto_20230930_1350'),
    ]

    operations = [
        migrations.AlterField(
            model_name='filmwork',
            name='file_path',
            field=models.TextField(null=True, verbose_name='file_path'),
        ),
    ]
