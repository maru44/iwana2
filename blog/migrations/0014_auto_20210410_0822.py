# Generated by Django 3.1.5 on 2021-04-09 23:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0013_offer_is_noticed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='offer',
            name='offer_mess',
            field=models.TextField(blank=True, max_length=400, null=True, verbose_name='メッセージ'),
        ),
    ]
