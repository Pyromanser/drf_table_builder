# Generated by Django 4.2 on 2023-04-15 15:02

from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields
import table_builder.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DynamicTable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('name', models.CharField(max_length=63, unique=True, validators=[table_builder.validators.validate_table_name], verbose_name='Table Name')),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DynamicColumn',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('name', models.CharField(max_length=59, unique=True, validators=[table_builder.validators.validate_column_name], verbose_name='Column name')),
                ('field_type', models.CharField(choices=[('Char', 'CharField'), ('Integer', 'IntegerField'), ('Boolean', 'BooleanField')], default='Char', max_length=100, verbose_name='Field type')),
                ('table', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='columns', to='table_builder.dynamictable', verbose_name='Table name')),
            ],
            options={
                'unique_together': {('name', 'table')},
            },
        ),
    ]
