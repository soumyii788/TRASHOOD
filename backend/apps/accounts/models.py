"""
accounts app – Custom user model, JWT auth, OTP, role validations.
"""
import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserRole(models.TextChoices):
    CUSTOMER = 'CUSTOMER', 'Customer'
    COLLECTOR = 'COLLECTOR', 'Collector'
    ADMIN = 'ADMIN', 'Admin'


class UserManager(BaseUserManager):
    def create_user(self, phone_number, role=UserRole.CUSTOMER, password=None, **extra):
        if not phone_number:
            raise ValueError("Phone number is required.")
        user = self.model(phone_number=phone_number, role=role, **extra)
        user.set_unusable_password()
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_social_user(self, provider, sub, email=None, role=UserRole.CUSTOMER, **extra):
        """Create a user authenticated via an external identity provider (Google/Apple)."""
        if not sub:
            raise ValueError("Social provider subject (sub) is required.")
        user = self.model(social_provider=provider, social_sub=sub, email=email,
                          role=role, is_verified=True, **extra)
        user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra):
        extra.setdefault('is_staff', True)
        extra.setdefault('is_superuser', True)
        user = self.create_user(phone_number, role=UserRole.ADMIN, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """
    Central user model. Authenticated by phone number + OTP, or via a
    social identity provider (Google / Apple).
    Role drives API access permissions.
    """

    class SocialProvider(models.TextChoices):
        GOOGLE = 'google', 'Google'
        APPLE = 'apple', 'Apple'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    social_provider = models.CharField(max_length=20, choices=SocialProvider.choices,
                                      null=True, blank=True)
    social_sub = models.CharField(max_length=255, null=True, blank=True)
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.CUSTOMER)
    is_verified = models.BooleanField(default=False)  # True after OTP verification
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['social_provider', 'social_sub'],
                condition=models.Q(social_sub__isnull=False),
                name='unique_social_identity',
            ),
        ]

    @property
    def login_identifier(self):
        """Human-readable identifier for display/admin."""
        return self.phone_number or self.email or str(self.id)

    def __str__(self):
        return f"{self.login_identifier} ({self.role})"


class OTPVerification(models.Model):
    """Stores short-lived OTPs for phone number verification."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otps')
    otp_code = models.CharField(max_length=6)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"OTP for {self.user.phone_number}"


class CollectorProfile(models.Model):
    """Extended profile for Collector role users."""

    class VehicleType(models.TextChoices):
        BIKE = 'BIKE', 'Bike'
        TEMPO = 'TEMPO', 'Tempo'
        TRUCK = 'TRUCK', 'Truck'

    class KycStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='collector_profile')
    vehicle_type = models.CharField(max_length=10, choices=VehicleType.choices, default=VehicleType.BIKE)
    kyc_status = models.CharField(max_length=10, choices=KycStatus.choices, default=KycStatus.PENDING)
    is_available = models.BooleanField(default=True)
    current_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    current_long = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    last_location_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Collector: {self.user.phone_number}"
