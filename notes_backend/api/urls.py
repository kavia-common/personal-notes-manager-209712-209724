from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import health, signup, login, NoteViewSet

router = DefaultRouter()
router.register(r'notes', NoteViewSet, basename='note')

urlpatterns = [
    path('health/', health, name='api-health'),
    path('auth/signup/', signup, name='api-signup'),
    path('auth/login/', login, name='api-login'),
    path('', include(router.urls)),
]
