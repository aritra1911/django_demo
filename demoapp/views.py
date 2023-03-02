from django.db.models import QuerySet
from rest_framework import (
    viewsets, mixins, authentication, parsers, renderers, permissions, status
)
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
        if not self.request.user.is_superuser:  # type: ignore
            queryset = queryset.filter(id=self.request.user.id) # type: ignore
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

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        customer = request.user

        existing_accounts: QuerySet[CustomerBankAccount] = \
            CustomerBankAccount.objects.filter(
                customer=customer,
                is_active=False,
                ifsc_code=request.data['ifsc_code'],
                account_number=request.data['account_number']
            )

        if existing_accounts.exists():
            existing_account: CustomerBankAccount = existing_accounts.get()

            # Deactivate the active account
            CustomerBankAccount.objects.filter(
                customer=customer,
                is_active=True
            ).update(is_active=False)

            # Activate the existing account
            existing_account.is_active = True
            existing_account.save()

            serializer = self.get_serializer(existing_account)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer) -> None:
        customer = self.request.user

        # Disable is_active for all other accounts of the customer
        accounts = CustomerBankAccount.objects.filter(customer=customer)
        accounts.update(is_active=False)

        serializer.save(customer=customer, is_active=True)

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return self.retrieve(request, *args, **kwargs)

    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        if kwargs.get('pk'):
            return Response({ 'detail': (
                'You are restricted to fetching only the active account. '
                'You cannot fetch an arbitrary account here.'
            )}, status=status.HTTP_404_NOT_FOUND)

        active_account: CustomerBankAccount = self.get_object()
        return Response(self.get_serializer(active_account).data)

    def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        if kwargs.get('pk'):
            return Response({ 'detail': (
                'You are restricted to updating only the active account. '
                'You cannot update any arbitrary account.'
            )}, status=status.HTTP_404_NOT_FOUND)

        active_account = self.get_object()
        serializer = self.get_serializer(
            active_account,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs) -> Response:
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs) -> Response:
        return self.update(request, *args, **kwargs)
