from rest_framework import serializers
from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'amount', 'txn_type', 'status', 'reference', 'created_at']
        read_only_fields = fields
