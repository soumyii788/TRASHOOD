from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collectorprofile',
            name='is_available',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='collectorprofile',
            name='last_location_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
