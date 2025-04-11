"""
Initial migration for PaymentTransaction model.
"""
from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Initial migration for PaymentTransaction model.
    """
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='PaymentTransaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gateway', models.CharField(choices=[('payme', 'Payme'), ('click', 'Click')], max_length=10)),
                ('transaction_id', models.CharField(max_length=255)),
                ('account_id', models.CharField(max_length=255)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=15)),
                ('state', models.IntegerField(choices=[(0, 'Created'), (1, 'Initiating'), (2, 'Successfully'), (-2, 'Cancelled after successful performed'), (-1, 'Cancelled during initiation')], default=0)),
                ('reason', models.IntegerField(blank=True, null=True, help_text='Reason for cancellation')),
                ('extra_data', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('performed_at', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('cancelled_at', models.DateTimeField(blank=True, db_index=True, null=True)),
            ],
            options={
                'verbose_name': 'Payment Transaction',
                'verbose_name_plural': 'Payment Transactions',
                'db_table': 'payments',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='paymenttransaction',
            index=models.Index(fields=['account_id'], name='payments_account_d4c2a8_idx'),
        ),
        migrations.AddIndex(
            model_name='paymenttransaction',
            index=models.Index(fields=['state'], name='payments_state_e0ceac_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='paymenttransaction',
            unique_together={('gateway', 'transaction_id')},
        ),
    ]
