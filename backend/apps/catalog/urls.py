from django.urls import path
from .views import ScrapCategoryListView, PublicScrapCategoryListView, ScrapCategoryDetailView

urlpatterns = [
    path('categories/', ScrapCategoryListView.as_view(), name='catalog-categories'),
    path('categories/<uuid:pk>/', ScrapCategoryDetailView.as_view(), name='catalog-category-detail'),
    path('public-categories/', PublicScrapCategoryListView.as_view(), name='catalog-public-categories'),
]
