# Generated by Django 5.2.4 on 2025-07-08 09:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system_manage', '0012_applytaskhistory_status_message'),
    ]

    operations = [
        migrations.AlterField(
            model_name='applytaskhistory',
            name='status_message',
            field=models.CharField(default='작업 준비 중 입니다.', max_length=255),
        ),
    ]
