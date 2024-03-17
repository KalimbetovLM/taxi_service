# Generated by Django 5.0.3 on 2024-03-16 07:43

import django.db.models.deletion
import project_taxi.utilities
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('shared', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('basemodel_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('given_stars', models.DecimalField(decimal_places=2, default=5, max_digits=3)),
                ('orders_count', models.IntegerField(default=0)),
                ('groups', models.ManyToManyField(related_name='client_groups', related_query_name='client_group', to='auth.group')),
                ('user_permissions', models.ManyToManyField(related_name='client_user_permissions', related_query_name='client_user_permission', to='auth.permission')),
            ],
            options={
                'abstract': False,
            },
            bases=('shared.basemodel',),
        ),
        migrations.CreateModel(
            name='ClientConfirmation',
            fields=[
                ('id', models.CharField(default=project_taxi.utilities.set_id, editable=False, max_length=15, primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=4)),
                ('expiration_time', models.DateTimeField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_confirmed', models.BooleanField(default=False)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='verify_codes', to='clients.client')),
            ],
        ),
    ]
