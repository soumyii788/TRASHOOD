from django.urls import path
from .views import WalletBalanceView, TransactionListView

urlpatterns = [
    path('balance/', WalletBalanceView.as_view(), name='wallet-balance'),
    path('transactions/', TransactionListView.as_view(), name='wallet-transactions'),
]
