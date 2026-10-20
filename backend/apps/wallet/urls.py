from django.urls import path
from .views import WalletBalanceView, TransactionListView, WalletWithdrawView

urlpatterns = [
    path('balance/', WalletBalanceView.as_view(), name='wallet-balance'),
    path('transactions/', TransactionListView.as_view(), name='wallet-transactions'),
    path('withdraw/', WalletWithdrawView.as_view(), name='wallet-withdraw'),
]
