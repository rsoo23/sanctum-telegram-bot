# Generated by Django 5.0.6 on 2024-07-10 06:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('agent', '0004_agent_energy_agent_luck_agent_mining_rate'),
    ]

    operations = [
        migrations.CreateModel(
            name='RewardZone',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('amount', models.IntegerField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('agent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reward_zones', to='agent.agent')),
            ],
            options={
                'db_table': 'reward_zones',
            },
        ),
    ]
