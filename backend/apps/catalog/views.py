from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import ScrapCategory
from .serializers import ScrapCategorySerializer


class ScrapCategoryListView(generics.ListAPIView):
    """GET /api/v1/catalog/categories/ – Sync latest prices to app."""
    queryset = ScrapCategory.objects.filter(is_active=True)
    serializer_class = ScrapCategorySerializer
    permission_classes = [IsAuthenticated]
