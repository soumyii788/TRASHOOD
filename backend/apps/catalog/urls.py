from django.urls import path
from .views import ScrapCategoryListView

urlpatterns = [
    path('categories/', ScrapCategoryListView.as_view(), name='catalog-categories'),
]
