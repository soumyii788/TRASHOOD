"""
Views for accounts app – OTP authentication and collector profile/location.
"""
import random
from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from common.permissions import IsCollector
from .models import User, OTPVerification, CollectorProfile, UserRole
from .serializers import (
    SendOTPSerializer, VerifyOTPSerializer,
    CollectorProfileSerializer, CollectorLocationSerializer,
    UserSerializer, AvailabilitySerializer,
)
from apps.customers.models import CustomerProfile
from apps.pickups.services import active_pickups_for_collector
from apps.tracking.broadcast import broadcast_location
from apps.notifications.tasks import send_sms_notification
from common.tasks import enqueue


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'user': UserSerializer(user).data,
    }


class SendOTPView(APIView):
    """POST /api/v1/auth/send-otp/ – Request OTP via SMS."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone_number']
        role = serializer.validated_data['role']

        user, created = User.objects.get_or_create(
            phone_number=phone,
            defaults={'role': role},
        )
        if created and role == UserRole.CUSTOMER:
            CustomerProfile.objects.get_or_create(user=user)
        if created and role == UserRole.COLLECTOR:
            CollectorProfile.objects.get_or_create(user=user)

        OTPVerification.objects.filter(user=user, is_used=False).update(is_used=True)

        otp_code = str(random.randint(100000, 999999))
        OTPVerification.objects.create(
            user=user,
            otp_code=otp_code,
            expires_at=timezone.now() + timedelta(minutes=10),
        )

        enqueue(send_sms_notification, phone, f'Trashhood OTP: {otp_code}. Valid for 10 minutes.')

        response_data = {'message': 'OTP sent successfully.'}
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
        otp.save(update_fields=['is_used'])
        user.is_verified = True
        user.save(update_fields=['is_verified'])

        if user.role == UserRole.COLLECTOR:
            CollectorProfile.objects.get_or_create(user=user)
        if user.role == UserRole.CUSTOMER:
            CustomerProfile.objects.get_or_create(user=user)

        return Response(get_tokens_for_user(user), status=status.HTTP_200_OK)


class MeView(APIView):
    """GET /api/v1/auth/me/ – Current user + role profile."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        payload = UserSerializer(request.user).data
        if request.user.role == UserRole.CUSTOMER:
            profile, _ = CustomerProfile.objects.get_or_create(user=request.user)
            from apps.customers.serializers import CustomerProfileSerializer
            payload['profile'] = CustomerProfileSerializer(profile).data
        elif request.user.role == UserRole.COLLECTOR:
            profile, _ = CollectorProfile.objects.get_or_create(user=request.user)
            payload['profile'] = CollectorProfileSerializer(profile).data
        return Response(payload)


class CollectorProfileView(RetrieveUpdateAPIView):
    """GET/PATCH /api/v1/collectors/profile/"""
    serializer_class = CollectorProfileSerializer
    permission_classes = [IsAuthenticated, IsCollector]

    def get_object(self):
        profile, _ = CollectorProfile.objects.get_or_create(user=self.request.user)
        return profile


class ToggleAvailabilityView(APIView):
    """POST /api/v1/collectors/availability/  {is_available: true}"""
    permission_classes = [IsAuthenticated, IsCollector]

    def post(self, request):
        serializer = AvailabilitySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        collector = request.user.collector_profile
        collector.is_available = serializer.validated_data['is_available']
        collector.save(update_fields=['is_available'])
        return Response(CollectorProfileSerializer(collector).data)


class UpdateLocationView(APIView):
    """POST /api/v1/collectors/location/ – Push GNSS coordinates + live broadcast."""
    permission_classes = [IsAuthenticated, IsCollector]

    def post(self, request):
        serializer = CollectorLocationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        collector = request.user.collector_profile
        collector.current_lat = serializer.validated_data['lat']
        collector.current_long = serializer.validated_data['long']
        collector.last_location_at = timezone.now()
        collector.save(update_fields=['current_lat', 'current_long', 'last_location_at'])

        for pickup in active_pickups_for_collector(collector):
            broadcast_location(
                pickup.id,
                collector.current_lat,
                collector.current_long,
                collector_id=collector.id,
            )
        return Response({
            'message': 'Location updated.',
            'lat': collector.current_lat,
            'long': collector.current_long,
            'last_location_at': collector.last_location_at,
        })
