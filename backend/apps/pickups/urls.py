from django.urls import path
from .views import RequestPickupView, PickupHistoryView

urlpatterns = [
    path('request/', RequestPickupView.as_view(), name='pickup-request'),
    path('history/', PickupHistoryView.as_view(), name='pickup-history'),
]
