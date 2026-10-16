from django.db.models import Sum, Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Transaction
from .serializers import TransactionSerializer


class WalletBalanceView(APIView):
    """GET /api/v1/wallet/balance/ – Total net balance."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        credits = Transaction.objects.filter(
            user=user, txn_type='CREDIT', status='SUCCESS'
        ).aggregate(total=Sum('amount'))['total'] or 0

        debits = Transaction.objects.filter(
            user=user, txn_type='DEBIT', status='SUCCESS'
        ).aggregate(total=Sum('amount'))['total'] or 0

        balance = credits - debits
        return Response({'balance': balance, 'currency': 'INR'})


class TransactionListView(generics.ListAPIView):
    """GET /api/v1/wallet/transactions/ – Payouts and charges ledger."""
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)
