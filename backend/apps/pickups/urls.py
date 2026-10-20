from django.urls import path
from .views import (
    RequestPickupView,
    PickupHistoryView,
    ActivePickupView,
    PickupDetailView,
    CancelPickupView,
)

urlpatterns = [
    path('request/', RequestPickupView.as_view(), name='pickup-request'),
    path('history/', PickupHistoryView.as_view(), name='pickup-history'),
    path('active/', ActivePickupView.as_view(), name='pickup-active'),
    path('<uuid:pk>/cancel/', CancelPickupView.as_view(), name='pickup-cancel'),
    path('<uuid:pk>/', PickupDetailView.as_view(), name='pickup-detail'),
]
