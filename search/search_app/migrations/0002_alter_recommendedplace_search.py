# Generated by Django 4.2.3 on 2025-03-05 04:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('search_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recommendedplace',
            name='search',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='places', to='search_app.searchhistory'),
        ),
    ]
