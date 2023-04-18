# Generated by Django 4.2 on 2023-04-18 11:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_alter_activity_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('calorie_goal', models.DecimalField(blank=True, decimal_places=1, max_digits=6)),
                ('weight', models.DecimalField(blank=True, decimal_places=1, max_digits=6)),
                ('height', models.DecimalField(blank=True, decimal_places=2, max_digits=6)),
                ('gender', models.CharField(blank=True, max_length=255)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
