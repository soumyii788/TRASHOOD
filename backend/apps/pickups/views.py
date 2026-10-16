from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from common.permissions import IsCustomer
from apps.customers.models import CustomerProfile
from .models import PickupRequest
from .serializers import PickupRequestSerializer, CreatePickupSerializer


class RequestPickupView(APIView):
    """POST /api/v1/pickups/request/ – Schedule a scrap collection job."""
    permission_classes = [IsAuthenticated, IsCustomer]

    def post(self, request):
        serializer = CreatePickupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        profile, _ = CustomerProfile.objects.get_or_create(user=request.user)
        pickup = serializer.save(customer=profile, status='REQUESTED')
        return Response(PickupRequestSerializer(pickup).data, status=status.HTTP_201_CREATED)


class PickupHistoryView(generics.ListAPIView):
    """GET /api/v1/pickups/history/ – View previous pickups."""
    serializer_class = PickupRequestSerializer
    permission_classes = [IsAuthenticated, IsCustomer]

    def get_queryset(self):
        profile, _ = CustomerProfile.objects.get_or_create(user=self.request.user)
        return PickupRequest.objects.filter(customer=profile)
