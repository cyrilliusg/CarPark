# urls.py
from django.urls import path
from .views import VehicleListAPIView, EnterpriseListAPIView, DriverListAPIView, ActiveDriverAPIView

urlpatterns = [
    # ...
    path('api/vehicles/', VehicleListAPIView.as_view(), name='vehicle-list'),
    path('api/enterprises/', EnterpriseListAPIView.as_view(), name='enterprise-list'),
    path('api/drivers/', DriverListAPIView.as_view(), name='driver-list'),
    path('api/vehicles/<int:vehicle_id>/active_driver/', ActiveDriverAPIView.as_view(), name='active-driver'),
]
