from django.urls import path
from .views import CustomerProfileView, AddressListCreateView

urlpatterns = [
    path('profile/', CustomerProfileView.as_view(), name='customer-profile'),
    path('addresses/', AddressListCreateView.as_view(), name='customer-addresses'),
]
