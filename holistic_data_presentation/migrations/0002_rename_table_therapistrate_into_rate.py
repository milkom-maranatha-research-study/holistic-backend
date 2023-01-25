# Generated by Django 3.2.16 on 2023-01-25 03:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('holistic_organization', '0001_initial'),
        ('holistic_data_presentation', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Rate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('churn_rate', 'Churn Rate'), ('retention_rate', 'Retention Rate')], max_length=16)),
                ('period_type', models.CharField(choices=[('weekly', 'Weekly'), ('monthly', 'Monthly'), ('yearly', 'Yearly')], max_length=8)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('value', models.FloatField()),
                ('organization', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='holistic_organization.organization')),
            ],
            options={
                'unique_together': {('organization', 'type', 'start_date', 'end_date', 'period_type')},
            },
        ),
        migrations.DeleteModel(
            name='TherapistRate',
        ),
    ]
