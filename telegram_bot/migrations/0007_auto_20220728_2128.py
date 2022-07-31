# Generated by Django 3.2.7 on 2022-07-28 21:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('telegram_bot', '0006_alter_telegramusersettings_telegram_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='telegramusersettings',
            name='is_beat_currency',
        ),
        migrations.RemoveField(
            model_name='telegramusersettings',
            name='is_beat_weather',
        ),
        migrations.AddField(
            model_name='telegramusersettings',
            name='beat_currency',
            field=models.TimeField(null=True, verbose_name='Beat sending currency info'),
        ),
        migrations.AddField(
            model_name='telegramusersettings',
            name='beat_weather',
            field=models.TimeField(null=True, verbose_name='Beat sending weather info'),
        ),
    ]
