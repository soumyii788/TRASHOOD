from django.urls import path
from .views import (
    CollectorProfileView,
    UpdateLocationView,
    ToggleAvailabilityView,
)
from apps.pickups.views import (
    NearbyJobsView,
    AssignedJobsView,
    AcceptJobView,
    UpdateJobStatusView,
    WeighJobView,
    CompleteJobView,
)

urlpatterns = [
    path('profile/', CollectorProfileView.as_view(), name='collector-profile'),
    path('availability/', ToggleAvailabilityView.as_view(), name='collector-availability'),
    path('location/', UpdateLocationView.as_view(), name='collector-update-location'),
    path('jobs/nearby/', NearbyJobsView.as_view(), name='collector-nearby-jobs'),
    path('jobs/assigned/', AssignedJobsView.as_view(), name='collector-assigned-jobs'),
    path('jobs/<uuid:pk>/accept/', AcceptJobView.as_view(), name='collector-accept-job'),
    path('jobs/<uuid:pk>/status/', UpdateJobStatusView.as_view(), name='collector-update-status'),
    path('jobs/<uuid:pk>/weigh/', WeighJobView.as_view(), name='collector-weigh-job'),
    path('jobs/<uuid:pk>/complete/', CompleteJobView.as_view(), name='collector-complete-job'),
]
