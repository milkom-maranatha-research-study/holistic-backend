# Generated by Django 3.2.16 on 2022-11-28 03:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('holistic_organization', '0001_initial'),
        ('holistic_data_presentation', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='churnretentionrate',
            unique_together={('organization', 'type', 'start_date', 'end_date', 'period_type')},
        ),
        migrations.AlterUniqueTogether(
            name='numberoftherapist',
            unique_together={('organization', 'start_date', 'end_date', 'period_type', 'is_active')},
        ),
    ]