# Generated by Django 2.1.1 on 2019-08-25 23:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bad_joke', '0005_auto_20190825_2131'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chatuser',
            name='chat_id',
            field=models.BigIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='chatuser',
            name='group_chat_id',
            field=models.BigIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='joketext',
            name='group_chat_id',
            field=models.BigIntegerField(default=0),
        ),
    ]
