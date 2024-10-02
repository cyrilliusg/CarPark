# urls.py
from django.urls import path
from .views import VehicleListAPIView

urlpatterns = [
    # ...
    path('api/vehicles/', VehicleListAPIView.as_view(), name='vehicle-list'),
]
