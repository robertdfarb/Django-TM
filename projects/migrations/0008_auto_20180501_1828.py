# Generated by Django 2.0.4 on 2018-05-02 01:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0007_auto_20180501_1711'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='due_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
