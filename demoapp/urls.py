from django.urls import path, include
from rest_framework import routers
from demoapp import views

router = routers.DefaultRouter()
router.register(r'customers', views.CustomerViewSet, basename='customer')
router.register(r'banks', views.BankViewSet, basename='bank')

bank_detail = views.CustomerBankAccountViewSet.as_view({
    'get': 'retrieve',
    'post': 'create',
    'put': 'update',
    'patch': 'update',
})

urlpatterns = (
    path('api/', include(router.urls), name='api_root'),
    path('api/bank/', bank_detail, name='api_bank'),
    path(
        'api-token-auth/',
        views.ObtainAuthTokenWithEmail.as_view(),
        name='api_token_auth_with_email'
    ),
)
