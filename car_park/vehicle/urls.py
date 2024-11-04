# urls.py
from django.urls import path, include
from .views import VehicleListAPIView, EnterpriseListAPIView, DriverListAPIView, ActiveDriverAPIView, \
    ActiveVehicleDriverListAPIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    # ...
    path('api/vehicles/', VehicleListAPIView.as_view(), name='vehicle-list'),
    path('api/enterprises/', EnterpriseListAPIView.as_view(), name='enterprise-list'),
    path('api/drivers/', DriverListAPIView.as_view(), name='driver-list'),
    path('api/vehicles/<int:vehicle_id>/active_driver/', ActiveDriverAPIView.as_view(), name='active-driver'),
    path('api/active-vehicles/', ActiveVehicleDriverListAPIView.as_view(), name='active-vehicles'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api-auth/', include('rest_framework.urls')),

]
