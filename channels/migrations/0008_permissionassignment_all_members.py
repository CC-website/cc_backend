# Generated by Django 5.0.1 on 2024-02-28 10:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('channels', '0007_permissionassignment_members_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='permissionassignment',
            name='all_members',
            field=models.BooleanField(default=False),
        ),
    ]