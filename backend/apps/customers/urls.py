from django.urls import path
from .views import CustomerProfileView, AddressListCreateView, AddressDetailView

urlpatterns = [
    path('profile/', CustomerProfileView.as_view(), name='customer-profile'),
    path('addresses/', AddressListCreateView.as_view(), name='customer-addresses'),
    path('addresses/<uuid:pk>/', AddressDetailView.as_view(), name='customer-address-detail'),
]
