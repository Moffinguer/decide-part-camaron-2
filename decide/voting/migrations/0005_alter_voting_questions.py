# Generated by Django 4.1 on 2023-11-11 00:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0004_alter_voting_postproc_alter_voting_tally'),
    ]

    operations = [
        migrations.AddField(
            model_name='voting',
            name='questions',
            field=models.ManyToManyField(related_name='votings', to='voting.question'),
        ),
    ]