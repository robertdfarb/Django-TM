# Generated by Django 2.0.4 on 2018-05-02 00:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0006_auto_20180501_1709'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='status',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='taskstatus', to='projects.MasterTaskStatus'),
        ),
    ]
