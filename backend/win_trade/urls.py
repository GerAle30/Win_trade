from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from api.views import TraderViewSet, TradeViewSet, FollowerViewSet
from api.views_auth import (
    UserRegisterView, UserProfileViewSet, CustomTokenObtainPairView, VerifyTokenView
)

router = DefaultRouter()
router.register(r'traders', TraderViewSet)
router.register(r'trades', TradeViewSet)
router.register(r'followers', FollowerViewSet)

# Authentication routes
auth_router = DefaultRouter()
auth_router.register(r'auth/register', UserRegisterView, basename='auth-register')
auth_router.register(r'auth/profile', UserProfileViewSet, basename='auth-profile')
auth_router.register(r'auth/verify', VerifyTokenView, basename='auth-verify')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/', include(auth_router.urls)),
    path('api/auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api-auth/', include('rest_framework.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
