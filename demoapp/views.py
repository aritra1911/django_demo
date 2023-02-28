from rest_framework import viewsets, mixins, authentication, parsers, renderers, permissions
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.serializers import BaseSerializer
from demoapp.models import Customer, Bank, CustomerBankAccount
from demoapp.serializers import (
    AuthEmailTokenSerializer,
    CustomerSerializer,
    BankSerializer,
    CustomerBankAccountSerializer,
)
from typing import Any
from demoapp.permissions import IsCustomerAuthenticated


class ObtainAuthTokenWithEmail(APIView):
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (
        parsers.FormParser,
        parsers.MultiPartParser,
        parsers.JSONParser,
    )

    renderer_classes = (renderers.JSONRenderer,)

    def post(self, request):
        serializer = AuthEmailTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)

        return Response({'token': token.key})


class CustomerViewSet(mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (IsCustomerAuthenticated,)

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(id=self.request.user.id)
        return queryset


class BankViewSet(viewsets.ModelViewSet):
    queryset = Bank.objects.all()
    serializer_class = BankSerializer
    permission_classes = (permissions.AllowAny,)


class CustomerBankAccountViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerBankAccountSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self) -> CustomerBankAccount:
        return CustomerBankAccount.objects.get(
            customer=self.request.user,
            is_active=True
        )

    def perform_create(self, serializer: BaseSerializer) -> None:
        customer = self.request.user

        serializer.validated_data['customer'] = customer
        serializer.validated_data['is_active'] = True

        # Disable is_active for all other accounts of the customer
        accounts = CustomerBankAccount.objects.filter(customer=customer)
        accounts.update(is_active=False)

        serializer.save(customer=customer)

    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        active_account: CustomerBankAccount = self.get_object()
        return Response(self.get_serializer(active_account).data)

    def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        active_account = self.get_object()
        serializer = self.get_serializer(active_account, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
