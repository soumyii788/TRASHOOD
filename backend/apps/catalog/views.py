from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import ScrapCategory
from .serializers import ScrapCategorySerializer

_ACTIVE_QS = ScrapCategory.objects.filter(is_active=True)


class ScrapCategoryListView(generics.ListAPIView):
    """GET /api/v1/catalog/categories/ – Sync latest prices (authenticated)."""
    queryset = _ACTIVE_QS
    serializer_class = ScrapCategorySerializer
    permission_classes = [IsAuthenticated]


class PublicScrapCategoryListView(generics.ListAPIView):
    """GET /api/v1/catalog/public-categories/ – Price list for unauthenticated visitors."""
    queryset = _ACTIVE_QS
    serializer_class = ScrapCategorySerializer
    permission_classes = [AllowAny]
