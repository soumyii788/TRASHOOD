from django.urls import path
from .views import NearbyJobsView, AcceptJobView, UpdateJobStatusView, UpdateLocationView

urlpatterns = [
    path('jobs/nearby/', NearbyJobsView.as_view(), name='collector-nearby-jobs'),
    path('jobs/<uuid:pk>/accept/', AcceptJobView.as_view(), name='collector-accept-job'),
    path('jobs/<uuid:pk>/status/', UpdateJobStatusView.as_view(), name='collector-update-status'),
    path('location/', UpdateLocationView.as_view(), name='collector-update-location'),
]
