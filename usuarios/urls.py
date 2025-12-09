from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import UsuarioViewSet
from .views_auth import RegisterCompanyView, ChangePasswordView

router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet, basename='usuario')

urlpatterns = [
    # Autenticación JWT
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/register-company/', RegisterCompanyView.as_view(), name='register_company'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='change_password'),
    
    # Endpoints de usuarios
    path('', include(router.urls)),
]
