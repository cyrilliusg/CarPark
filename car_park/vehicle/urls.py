# urls.py
from django.urls import path, include
from .views import (
    VehicleListCreateAPIView,
    VehicleRetrieveUpdateDestroyAPIView,
    EnterpriseListCreateAPIView,
    EnterpriseRetrieveUpdateDestroyAPIView,
    DriverListCreateAPIView,
    DriverRetrieveUpdateDestroyAPIView,
    ActiveDriverAPIView,
    ActiveVehicleDriverListAPIView,
    api_login,
    login_view,
    enterprise_list_view
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # ...
    # Маршруты для Vehicle
    path('api/vehicles/', VehicleListCreateAPIView.as_view(), name='vehicle-list-create'),
    path('api/vehicles/<int:pk>/', VehicleRetrieveUpdateDestroyAPIView.as_view(), name='vehicle-detail'),

    # Маршруты для Enterprise
    path('api/enterprises/', EnterpriseListCreateAPIView.as_view(), name='enterprise-list-create'),
    path('api/enterprises/<int:pk>/', EnterpriseRetrieveUpdateDestroyAPIView.as_view(), name='enterprise-detail'),

    # Маршруты для Driver
    path('api/drivers/', DriverListCreateAPIView.as_view(), name='driver-list-create'),
    path('api/drivers/<int:pk>/', DriverRetrieveUpdateDestroyAPIView.as_view(), name='driver-detail'),

    path('api/vehicles/<int:vehicle_id>/active_driver/', ActiveDriverAPIView.as_view(), name='active-driver'),
    path('api/active-vehicles/', ActiveVehicleDriverListAPIView.as_view(), name='active-vehicles'),

    # Аутентификация
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('api-auth/', include('rest_framework.urls')),
    path('api/login/', api_login, name='api-login'),

    path('login/', login_view, name='login-view'),
    path('enterprises/', enterprise_list_view, name='enterprise-list-view'),

]
