from django.urls import path, include
from rest_framework import routers
from demoapp import views

router = routers.DefaultRouter()
router.register(r'customers', views.CustomerViewSet, basename='customer')

urlpatterns = (
    path('api/', include(router.urls), name='api'),
    path(
        'api-token-auth/',
        views.ObtainAuthTokenWithEmail.as_view(),
        name='api_token_auth_with_email'
    ),
)
