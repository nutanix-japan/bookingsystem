# Generated by Django 2.2.15 on 2020-08-24 02:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('modelNumber', models.CharField(blank=True, max_length=100, verbose_name='Model Number')),
                ('serialNumber', models.CharField(blank=True, max_length=100, verbose_name='Serial Number')),
                ('installationDate', models.DateField(blank=True, null=True, verbose_name='Installation Date')),
                ('expirationDate', models.DateField(blank=True, null=True, verbose_name='Expiration Date')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('note', models.TextField(blank=True, verbose_name='Note')),
                ('ownerGroup', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='account.Group')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
    ]