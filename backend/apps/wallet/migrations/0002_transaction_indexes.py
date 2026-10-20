from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallet', '0001_initial'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='transaction',
            index=models.Index(fields=['user', 'status'], name='wallet_txn_user_status_idx'),
        ),
        migrations.AddIndex(
            model_name='transaction',
            index=models.Index(fields=['reference'], name='wallet_txn_reference_idx'),
        ),
    ]
