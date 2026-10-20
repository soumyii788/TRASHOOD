from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import ScrapCategory
from .serializers import ScrapCategorySerializer


class ScrapCategoryListView(generics.ListAPIView):
    """GET /api/v1/catalog/categories/ – Sync latest prices (authenticated)."""
    queryset = ScrapCategory.objects.filter(is_active=True)
    serializer_class = ScrapCategorySerializer
    permission_classes = [IsAuthenticated]


class PublicScrapCategoryListView(generics.ListAPIView):
    """GET /api/v1/catalog/public-categories/ – Price list for unauthenticated visitors."""
    queryset = ScrapCategory.objects.filter(is_active=True)
    serializer_class = ScrapCategorySerializer
    permission_classes = [AllowAny]


class ScrapCategoryDetailView(generics.RetrieveAPIView):
    """GET /api/v1/catalog/categories/<id>/"""
    queryset = ScrapCategory.objects.filter(is_active=True)
    serializer_class = ScrapCategorySerializer
    permission_classes = [AllowAny]
