# Generated by Django 5.0.1 on 2024-02-24 08:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('channels', '0005_alter_permission_permission_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='permission',
            name='permission_type',
            field=models.IntegerField(choices=[(0, 'Delete'), (1, 'Create'), (2, 'Update'), (3, 'Is super admin'), (4, 'Add member'), (5, 'Remove member')]),
        ),
    ]
