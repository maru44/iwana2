# Generated by Django 3.1.5 on 2021-02-03 03:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0007_auto_20210203_0307'),
    ]

    operations = [
        migrations.AddField(
            model_name='wanted',
            name='slug',
            field=models.SlugField(blank=True, max_length=16, null=True, unique=True, verbose_name='slug'),
        ),
        migrations.AlterField(
            model_name='wanted',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
