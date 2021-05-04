# Generated by Django 3.1.7 on 2021-04-09 08:11

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('wildSightApp', '0013_auto_20210408_1127'),
    ]

    operations = [
        migrations.AlterField(
            model_name='raw_sighting',
            name='voted_by',
            field=models.ManyToManyField(related_name='Voter', to=settings.AUTH_USER_MODEL),
        ),
    ]