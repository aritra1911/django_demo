from rest_framework import viewsets, exceptions, authentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from demoapp.models import Customer
from demoapp.serializers import CustomerSerializer
from demoapp.permissions import IsCustomerAuthenticated


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        print(serializer.validated_data)
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = (IsCustomerAuthenticated,)

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(id=self.request.user.id)
        return queryset

    # Disallow DELETE on this ViewSet
    def destroy(self, request, *args, **kwargs):
        raise exceptions.MethodNotAllowed(
            request.method, detail='DELETE method is not allowed.'
        )
