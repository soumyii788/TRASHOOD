from decimal import Decimal

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pickups', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pickuprequest',
            name='status',
            field=models.CharField(
                choices=[
                    ('REQUESTED', 'Requested'),
                    ('ASSIGNED', 'Assigned'),
                    ('ON_THE_WAY', 'On The Way'),
                    ('ARRIVED', 'Arrived'),
                    ('WEIGHING', 'Weighing'),
                    ('COMPLETED', 'Completed'),
                    ('CANCELLED', 'Cancelled'),
                ],
                default='REQUESTED',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='pickuprequest',
            name='estimated_payout',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10),
        ),
        migrations.AddField(
            model_name='pickuprequest',
            name='cancellation_reason',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='pickuprequest',
            name='assigned_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='pickuprequest',
            name='started_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='pickuprequest',
            name='arrived_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='pickuprequest',
            name='completed_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='pickuprequest',
            name='cancelled_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='pickupitem',
            name='estimated_weight_kg',
            field=models.DecimalField(decimal_places=3, default=Decimal('0.000'), max_digits=8),
        ),
        migrations.AddField(
            model_name='pickupitem',
            name='unit_price',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=8),
        ),
        migrations.AlterUniqueTogether(
            name='pickupitem',
            unique_together={('pickup', 'category')},
        ),
        migrations.AddIndex(
            model_name='pickuprequest',
            index=models.Index(fields=['status'], name='pickups_pic_status_idx'),
        ),
        migrations.AddIndex(
            model_name='pickuprequest',
            index=models.Index(fields=['scheduled_time'], name='pickups_pic_schedul_idx'),
        ),
        migrations.CreateModel(
            name='PickupEvent',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('from_status', models.CharField(blank=True, max_length=20)),
                ('to_status', models.CharField(max_length=20)),
                ('note', models.CharField(blank=True, max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('actor', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='pickup_events',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('pickup', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='events',
                    to='pickups.pickuprequest',
                )),
            ],
            options={
                'ordering': ['created_at'],
            },
        ),
    ]
