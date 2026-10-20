from django.db.models import Sum
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from decimal import Decimal

from .models import Transaction
from .serializers import TransactionSerializer


class WalletBalanceView(APIView):
    """GET /api/v1/wallet/balance/ – Total net balance plus pending."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        qs = Transaction.objects.filter(user=user)
        credits = qs.filter(
            txn_type=Transaction.TxnType.CREDIT, status=Transaction.TxnStatus.SUCCESS
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        debits = qs.filter(
            txn_type=Transaction.TxnType.DEBIT, status=Transaction.TxnStatus.SUCCESS
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        pending = qs.filter(status=Transaction.TxnStatus.PENDING).aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0')

        return Response({
            'balance': credits - debits,
            'pending': pending,
            'lifetime_credits': credits,
            'currency': 'INR',
        })


class TransactionListView(generics.ListAPIView):
    """GET /api/v1/wallet/transactions/ – Payouts and charges ledger."""
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Transaction.objects.filter(user=self.request.user)
        txn_type = self.request.query_params.get('txn_type')
        txn_status = self.request.query_params.get('status')
        if txn_type:
            qs = qs.filter(txn_type=txn_type.upper())
        if txn_status:
            qs = qs.filter(status=txn_status.upper())
        return qs


class WalletWithdrawView(APIView):
    """POST /api/v1/wallet/withdraw/ – Request a debit of available balance."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            amount = Decimal(str(request.data.get('amount', '0')))
        except Exception as exc:
            raise ValidationError({'amount': 'Invalid amount.'}) from exc
        if amount <= 0:
            raise ValidationError({'amount': 'Amount must be greater than zero.'})

        credits = Transaction.objects.filter(
            user=request.user, txn_type='CREDIT', status='SUCCESS'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        debits = Transaction.objects.filter(
            user=request.user, txn_type='DEBIT', status='SUCCESS'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        balance = credits - debits
        if amount > balance:
            raise ValidationError({'amount': 'Insufficient wallet balance.'})

        txn = Transaction.objects.create(
            user=request.user,
            amount=amount,
            txn_type=Transaction.TxnType.DEBIT,
            status=Transaction.TxnStatus.PENDING,
            reference='withdrawal_request',
        )
        return Response(TransactionSerializer(txn).data, status=status.HTTP_201_CREATED)
