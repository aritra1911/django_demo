from django.db import OperationalError
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
from typing import Any, Final, Optional
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

    def post(self, request: Request) -> Response:
        serializer = AuthEmailTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        try:
            token, created = Token.objects.get_or_create(user=user)
        except OperationalError as oe:
            return Response(data={
                "message": (f"An error occurred while trying to fetch token "
                            f"for customer: { str(oe) }")
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({ 'token': token.key })


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
        customer: Customer = self.request.user                  # type: ignore
        if not customer.is_superuser:
            queryset = Customer.get_queryset_by_id(customer.id) # type: ignore
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
        customer: Customer = self.request.user                  # type: ignore
        return CustomerBankAccount.get_active_account(customer)

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        customer: Customer = request.user                       # type: ignore

        # Check if it is possible to fetch an existing inactive account
        # of the customer with the same ifsc_code and account_number of
        # the new account being created.
        try:
            existing_account: Optional[CustomerBankAccount] = \
                CustomerBankAccount.get_existing_account(
                    customer=customer,
                    ifsc_code=request.data['ifsc_code'],
                    account_number=request.data['account_number']
                )
        except OperationalError as oe:
            return Response(data={
                "message": (f"An error occurred while trying to get existing "
                            f"accounts: { str(oe) }")
            }, status=status.HTTP_400_BAD_REQUEST)

        if existing_account:
            # If we found such an account, turn it into the active
            # account instead of creating a new one.
            try:
                CustomerBankAccount.deactivate_active_account(customer)
            except OperationalError as oe:
                return Response(data={
                    "message": (f"An error occurred while trying to deactivate "
                                f"the active account: { str(oe) }")
                }, status=status.HTTP_400_BAD_REQUEST)
            try:
                existing_account.activate()
            except OperationalError as oe:
                return Response(data={
                    "message": (f"An error occurred while trying to activate "
                                f"the existing account: { str(oe) }")
                }, status=status.HTTP_400_BAD_REQUEST)
            serializer = self.get_serializer(existing_account)
        else:
            # Create new account
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            try:
                self.perform_create(serializer)
            except OperationalError as oe:
                return Response(data={
                    "message": (f"An error occurred while trying to create "
                                f"account: { str(oe) }")
                }, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer) -> None:
        customer: Customer = self.request.user                  # type: ignore
        CustomerBankAccount.deactivate_active_account(customer)
        serializer.save(customer=customer, is_active=True)

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return self.retrieve(request, *args, **kwargs)

    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        if kwargs.get('pk'):
            return Response({ 'detail': (
                'You are restricted to fetching only the active account. '
                'You cannot fetch an arbitrary account here.'
            )}, status=status.HTTP_404_NOT_FOUND)

        try:
            active_account: CustomerBankAccount = self.get_object()
        except OperationalError as oe:
            return Response(data={
                "message": (f"An error occurred while trying to retrieve "
                            f"account details: { str(oe) }")
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            return Response(self.get_serializer(active_account).data)
        except OperationalError as oe:
            return Response(data={
                "message": (f"An error occurred while trying to serialize "
                            f"account details: { str(oe) }")
            }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        if kwargs.get('pk'):
            return Response({ 'detail': (
                'You are restricted to updating only the active account. '
                'You cannot update any arbitrary account.'
            )}, status=status.HTTP_404_NOT_FOUND)

        try:
            active_account = self.get_object()
        except OperationalError as oe:
            return Response(data={
                "message": (f"An error occurred while trying to fetch active "
                            f"account: { str(oe) }")
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(
            active_account,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)

        try:
            self.perform_update(serializer)
        except OperationalError as oe:
            return Response(data={
                "message": (f"An error occurred while trying to update details "
                            f"of active account: { str(oe) }")
            }, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs) -> Response:
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs) -> Response:
        return self.update(request, *args, **kwargs)
