from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TraderViewSet, TradeViewSet, FollowerViewSet

router = DefaultRouter()
router.register(r'traders', TraderViewSet, basename='trader')
router.register(r'trades', TradeViewSet, basename='trade')
router.register(r'followers', FollowerViewSet, basename='follower')

urlpatterns = [
    path('', include(router.urls)),
]
