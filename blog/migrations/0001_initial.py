# Generated by Django 3.1.5 on 2021-01-23 12:01

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Plat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.CharField(max_length=24, verbose_name='Slug')),
                ('name', models.CharField(max_length=24, verbose_name='名前')),
                ('host', models.CharField(blank=True, max_length=48, null=True, verbose_name='ホストURL')),
            ],
        ),
        migrations.CreateModel(
            name='Wanted',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('want_name', models.CharField(max_length=36, verbose_name='欲しいもの')),
                ('posted', models.DateTimeField(auto_now_add=True, verbose_name='投稿日')),
                ('picture', models.ImageField(blank=True, null=True, upload_to='wanted', verbose_name='画像')),
                ('is_gotten', models.BooleanField(default=False, verbose_name='取得済み')),
                ('want_intro', models.TextField(blank=True, max_length=800, null=True, verbose_name='説明')),
                ('want_price', models.IntegerField(blank=True, null=True, verbose_name='値段')),
            ],
        ),
    ]
