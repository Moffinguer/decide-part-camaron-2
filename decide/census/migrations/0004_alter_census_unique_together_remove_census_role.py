# Generated by Django 4.1 on 2023-11-11 01:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('census', '0003_alter_census_role'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='census',
            unique_together={('voting_id', 'voter_id')},
        ),
        migrations.RemoveField(
            model_name='census',
            name='role',
        ),
    ]
