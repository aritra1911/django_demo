from django.urls import path, include
from rest_framework import routers
from demoapp import views

router = routers.DefaultRouter()
router.register(r'customers', views.CustomerViewSet, basename='customer')

urlpatterns = (
    path('', include(router.urls)),
    path('api-token-auth/', views.CustomAuthToken.as_view()),
)
