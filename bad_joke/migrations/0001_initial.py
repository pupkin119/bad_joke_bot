# Generated by Django 2.1.1 on 2019-08-17 17:10

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ChatUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chat_id', models.IntegerField(default=0)),
                ('first_name', models.CharField(blank=True, max_length=140, null=True)),
                ('last_name', models.CharField(blank=True, max_length=140, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_answer', models.BooleanField(default=False)),
                ('is_in_game', models.BooleanField(default=False)),
                ('is_winner', models.BooleanField(default=True)),
                ('answer', models.CharField(blank=True, max_length=500, null=True)),
                ('score', models.IntegerField(default=0)),
            ],
        ),
    ]
