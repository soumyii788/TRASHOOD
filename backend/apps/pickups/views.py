from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.permissions import IsCustomer, IsCollector
from apps.customers.models import CustomerProfile
from apps.pickups.models import PickupRequest
from apps.pickups.serializers import (
    PickupRequestSerializer,
    CreatePickupSerializer,
    CancelPickupSerializer,
    JobStatusSerializer,
    WeighItemsSerializer,
)
from apps.pickups import services


def _customer_profile(user):
    profile, _ = CustomerProfile.objects.get_or_create(user=user)
    return profile


def _pickup_qs():
    return PickupRequest.objects.select_related(
        'customer__user', 'assigned_collector__user', 'pickup_address'
    ).prefetch_related('items__category', 'events__actor')


class RequestPickupView(APIView):
    """POST /api/v1/pickups/request/ – Schedule a scrap collection job."""
    permission_classes = [IsAuthenticated, IsCustomer]

    def post(self, request):
        serializer = CreatePickupSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        profile = _customer_profile(request.user)
        pickup = services.create_pickup(
            customer=profile,
            pickup_address=serializer.validated_data.get('pickup_address'),
            scheduled_time=serializer.validated_data['scheduled_time'],
            notes=serializer.validated_data.get('notes', ''),
            items=serializer.validated_data.get('items'),
        )
        pickup = _pickup_qs().get(pk=pickup.pk)
        return Response(PickupRequestSerializer(pickup).data, status=status.HTTP_201_CREATED)


class PickupHistoryView(generics.ListAPIView):
    """GET /api/v1/pickups/history/ – View previous pickups. Optional ?status="""
    serializer_class = PickupRequestSerializer
    permission_classes = [IsAuthenticated, IsCustomer]

    def get_queryset(self):
        profile = _customer_profile(self.request.user)
        qs = _pickup_qs().filter(customer=profile)
        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter.upper())
        return qs


class ActivePickupView(generics.ListAPIView):
    """GET /api/v1/pickups/active/ – In-flight pickups for the customer."""
    serializer_class = PickupRequestSerializer
    permission_classes = [IsAuthenticated, IsCustomer]

    def get_queryset(self):
        profile = _customer_profile(self.request.user)
        return _pickup_qs().filter(
            customer=profile,
            status__in=[
                PickupRequest.Status.REQUESTED,
                PickupRequest.Status.ASSIGNED,
                PickupRequest.Status.ON_THE_WAY,
                PickupRequest.Status.ARRIVED,
                PickupRequest.Status.WEIGHING,
            ],
        )


class PickupDetailView(APIView):
    """GET /api/v1/pickups/<id>/ – Pickup detail for customer or assigned collector."""
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        pickup = get_object_or_404(_pickup_qs(), pk=pk)
        user = request.user
        is_owner = hasattr(user, 'customer_profile') and pickup.customer_id == user.customer_profile.id
        is_assignee = (
            hasattr(user, 'collector_profile')
            and pickup.assigned_collector_id == user.collector_profile.id
        )
        if not (is_owner or is_assignee or user.role == 'ADMIN'):
            raise PermissionDenied('You cannot view this pickup.')
        return Response(PickupRequestSerializer(pickup).data)


class CancelPickupView(APIView):
    """POST /api/v1/pickups/<id>/cancel/"""
    permission_classes = [IsAuthenticated, IsCustomer]

    def post(self, request, pk):
        profile = _customer_profile(request.user)
        pickup = get_object_or_404(_pickup_qs(), pk=pk, customer=profile)
        serializer = CancelPickupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pickup = services.cancel_pickup(
            pickup=pickup,
            actor=request.user,
            reason=serializer.validated_data.get('reason', ''),
        )
        pickup = _pickup_qs().get(pk=pickup.pk)
        return Response(PickupRequestSerializer(pickup).data)


# --------------- Collector job ops ---------------

class NearbyJobsView(APIView):
    """GET /api/v1/collectors/jobs/nearby/?radius_km=&lat=&long="""
    permission_classes = [IsAuthenticated, IsCollector]

    def get(self, request):
        collector = request.user.collector_profile
        radius = request.query_params.get('radius_km', 15)
        lat = request.query_params.get('lat', collector.current_lat)
        lon = request.query_params.get('long', collector.current_long)
        try:
            radius = float(radius) if radius is not None else None
        except (TypeError, ValueError):
            radius = 15
        jobs = services.nearby_jobs(collector=collector, radius_km=radius, lat=lat, lon=lon)
        return Response(PickupRequestSerializer(jobs, many=True).data)


class AssignedJobsView(generics.ListAPIView):
    """GET /api/v1/collectors/jobs/assigned/"""
    serializer_class = PickupRequestSerializer
    permission_classes = [IsAuthenticated, IsCollector]

    def get_queryset(self):
        return _pickup_qs().filter(assigned_collector=self.request.user.collector_profile).exclude(
            status__in=[PickupRequest.Status.CANCELLED]
        )


class AcceptJobView(APIView):
    """POST /api/v1/collectors/jobs/:id/accept/"""
    permission_classes = [IsAuthenticated, IsCollector]

    def post(self, request, pk):
        pickup = services.accept_job(pickup_id=pk, collector=request.user.collector_profile)
        pickup = _pickup_qs().get(pk=pickup.pk)
        return Response(PickupRequestSerializer(pickup).data)


class UpdateJobStatusView(APIView):
    """PATCH /api/v1/collectors/jobs/:id/status/ – body optional {status, note}."""
    permission_classes = [IsAuthenticated, IsCollector]

    def patch(self, request, pk):
        pickup = get_object_or_404(_pickup_qs(), pk=pk)
        serializer = JobStatusSerializer(data=request.data or {})
        serializer.is_valid(raise_exception=True)
        pickup = services.collector_advance(
            pickup=pickup,
            collector=request.user.collector_profile,
            to_status=serializer.validated_data.get('status'),
            note=serializer.validated_data.get('note', ''),
        )
        pickup = _pickup_qs().get(pk=pickup.pk)
        return Response(PickupRequestSerializer(pickup).data)


class WeighJobView(APIView):
    """POST /api/v1/collectors/jobs/:id/weigh/"""
    permission_classes = [IsAuthenticated, IsCollector]

    def post(self, request, pk):
        pickup = get_object_or_404(_pickup_qs(), pk=pk)
        serializer = WeighItemsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pickup = services.weigh_items(
            pickup=pickup,
            collector=request.user.collector_profile,
            items=serializer.validated_data['items'],
        )
        pickup = _pickup_qs().get(pk=pickup.pk)
        return Response(PickupRequestSerializer(pickup).data)


class CompleteJobView(APIView):
    """POST /api/v1/collectors/jobs/:id/complete/ – finalise + settle wallet."""
    permission_classes = [IsAuthenticated, IsCollector]

    def post(self, request, pk):
        pickup = get_object_or_404(_pickup_qs(), pk=pk)
        if pickup.assigned_collector_id != request.user.collector_profile.id:
            raise PermissionDenied('This job is not assigned to you.')
        pickup = services.complete_pickup(pickup=pickup, actor=request.user)
        pickup = _pickup_qs().get(pk=pickup.pk)
        return Response(PickupRequestSerializer(pickup).data)
