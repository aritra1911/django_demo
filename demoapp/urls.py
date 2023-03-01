from django.urls import path, include
from rest_framework import routers
from demoapp import views

router = routers.DefaultRouter()
router.register(r'customers', views.CustomerViewSet, basename='customer')
router.register(r'banks', views.BankViewSet, basename='bank')
router.register(
    prefix=r'bank',
    viewset=views.CustomerBankAccountViewSet,
    basename='active-bank'
)

urlpatterns = (
    path('api/', include(router.urls), name='api_root'),
    path(
        'api-token-auth/',
        views.ObtainAuthTokenWithEmail.as_view(),   # type: ignore
        name='api_token_auth_with_email'
    ),
)
