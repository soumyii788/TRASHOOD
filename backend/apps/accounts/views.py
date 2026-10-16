"""
Views for accounts app – OTP authentication and collector ops.
"""
import random
from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from common.permissions import IsCollector
from .models import User, OTPVerification, CollectorProfile
from .serializers import (
    SendOTPSerializer, VerifyOTPSerializer,
    CollectorProfileSerializer, CollectorLocationSerializer,
)
from apps.pickups.models import PickupRequest


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class SendOTPView(APIView):
    """POST /api/v1/auth/send-otp/ – Request OTP via SMS."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone_number']
        role = serializer.validated_data['role']

        user, _ = User.objects.get_or_create(
            phone_number=phone,
            defaults={'role': role}
        )

        # Invalidate all previous unused OTPs for this user
        OTPVerification.objects.filter(user=user, is_used=False).update(is_used=True)

        otp_code = str(random.randint(100000, 999999))
        OTPVerification.objects.create(
            user=user,
            otp_code=otp_code,
            expires_at=timezone.now() + timedelta(minutes=30),
        )

        print(f"[DEV] OTP for {phone}: {otp_code}")

        response_data = {'message': 'OTP sent successfully.'}
        # In DEBUG mode, return OTP directly in the response
        if getattr(settings, 'DEBUG', False):
            response_data['otp'] = otp_code

        return Response(response_data, status=status.HTTP_200_OK)


class VerifyOTPView(APIView):
    """POST /api/v1/auth/verify-otp/ – Verify OTP and receive JWT."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone_number']
        otp_code = serializer.validated_data['otp_code']

        try:
            user = User.objects.get(phone_number=phone)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        otp = OTPVerification.objects.filter(
            user=user,
            otp_code=otp_code,
            is_used=False,
            expires_at__gte=timezone.now(),
        ).last()

        if not otp:
            return Response({'error': 'Invalid or expired OTP.'}, status=status.HTTP_400_BAD_REQUEST)

        otp.is_used = True
        otp.save()
        user.is_verified = True
        user.save()

        # Auto-create collector profile if role is COLLECTOR
        if user.role == 'COLLECTOR':
            CollectorProfile.objects.get_or_create(user=user)

        return Response(get_tokens_for_user(user), status=status.HTTP_200_OK)


# --------------- Collector Views ---------------

class NearbyJobsView(APIView):
    """GET /api/v1/collectors/jobs/nearby/ – Unassigned pickups."""
    permission_classes = [IsAuthenticated, IsCollector]

    def get(self, request):
        jobs = PickupRequest.objects.filter(status='REQUESTED', assigned_collector=None)
        from apps.pickups.serializers import PickupRequestSerializer
        serializer = PickupRequestSerializer(jobs, many=True)
        return Response(serializer.data)


class AcceptJobView(APIView):
    """POST /api/v1/collectors/jobs/:id/accept/ – Lock a pickup."""
    permission_classes = [IsAuthenticated, IsCollector]

    def post(self, request, pk):
        try:
            job = PickupRequest.objects.get(pk=pk, status='REQUESTED', assigned_collector=None)
        except PickupRequest.DoesNotExist:
            return Response({'error': 'Job not available.'}, status=status.HTTP_404_NOT_FOUND)

        collector = request.user.collector_profile
        job.assigned_collector = collector
        job.status = 'ASSIGNED'
        job.save()
        return Response({'message': 'Job accepted.'}, status=status.HTTP_200_OK)


class UpdateJobStatusView(APIView):
    """PATCH /api/v1/collectors/jobs/:id/status/ – Progress job."""
    permission_classes = [IsAuthenticated, IsCollector]

    VALID_TRANSITIONS = {
        'ASSIGNED': 'ON_THE_WAY',
        'ON_THE_WAY': 'COMPLETED',
    }

    def patch(self, request, pk):
        try:
            job = PickupRequest.objects.get(pk=pk, assigned_collector=request.user.collector_profile)
        except PickupRequest.DoesNotExist:
            return Response({'error': 'Job not found.'}, status=status.HTTP_404_NOT_FOUND)

        next_status = self.VALID_TRANSITIONS.get(job.status)
        if not next_status:
            return Response({'error': 'Cannot transition from this status.'}, status=status.HTTP_400_BAD_REQUEST)

        job.status = next_status
        job.save()
        return Response({'status': job.status})


class UpdateLocationView(APIView):
    """POST /api/v1/collectors/location/ – Push GNSS coordinates."""
    permission_classes = [IsAuthenticated, IsCollector]

    def post(self, request):
        serializer = CollectorLocationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        collector = request.user.collector_profile
        collector.current_lat = serializer.validated_data['lat']
        collector.current_long = serializer.validated_data['long']
        collector.save()
        return Response({'message': 'Location updated.'})
