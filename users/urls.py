from django.urls import path, include
from rest_framework.routers import DefaultRouter

from config import urls
from .views import UserViewSet, RegisterView

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
    path('', include('djoser.urls')),
    path('', include('djoser.urls.authtoken')),
]