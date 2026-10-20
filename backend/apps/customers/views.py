from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from common.permissions import IsCustomer
from .models import CustomerProfile, Address
from .serializers import CustomerProfileSerializer, AddressSerializer


class CustomerProfileView(generics.RetrieveUpdateAPIView):
    """GET/PUT/PATCH /api/v1/customers/profile/"""
    serializer_class = CustomerProfileSerializer
    permission_classes = [IsAuthenticated, IsCustomer]

    def get_object(self):
        profile, _ = CustomerProfile.objects.get_or_create(user=self.request.user)
        return profile


class AddressListCreateView(generics.ListCreateAPIView):
    """GET/POST /api/v1/customers/addresses/"""
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated, IsCustomer]

    def get_queryset(self):
        profile, _ = CustomerProfile.objects.get_or_create(user=self.request.user)
        return Address.objects.filter(customer=profile)

    def perform_create(self, serializer):
        profile, _ = CustomerProfile.objects.get_or_create(user=self.request.user)
        serializer.save(customer=profile)


class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PUT/PATCH/DELETE /api/v1/customers/addresses/<id>/"""
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated, IsCustomer]

    def get_queryset(self):
        profile, _ = CustomerProfile.objects.get_or_create(user=self.request.user)
        return Address.objects.filter(customer=profile)
