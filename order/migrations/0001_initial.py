# Generated by Django 5.0.3 on 2024-03-23 09:24

import django.db.models.deletion
import project_taxi.utilities
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('clients', '0001_initial'),
        ('drivers', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.CharField(default=project_taxi.utilities.set_id, max_length=15, primary_key=True, serialize=False, unique=True)),
                ('pickup_location', models.CharField(max_length=100)),
                ('dropoff_location', models.CharField(max_length=100)),
                ('order_status', models.CharField(choices=[('coming', 'coming'), ('way', 'way'), ('finish', 'finish'), ('cancel', 'cancel')], default='coming', max_length=6)),
                ('start_time', models.DateTimeField(auto_now_add=True)),
                ('end_time', models.DateTimeField(auto_now=True)),
                ('total_time', models.DateTimeField(null=True)),
                ('cost', models.DecimalField(decimal_places=5, default=0, max_digits=10)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='client', to='clients.client')),
                ('driver', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='driver', to='drivers.driver')),
            ],
        ),
    ]
