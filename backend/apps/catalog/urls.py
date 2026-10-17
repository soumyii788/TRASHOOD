from django.urls import path
from .views import ScrapCategoryListView, PublicScrapCategoryListView

urlpatterns = [
    path('categories/', ScrapCategoryListView.as_view(), name='catalog-categories'),
    path('public-categories/', PublicScrapCategoryListView.as_view(), name='catalog-public-categories'),
]
