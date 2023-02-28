from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions, serializers
from demoapp.models import Customer, Bank, CustomerBankAccount
from typing import Any


MAX_ACCOUNTS_PER_CUSTOMER = 4


class AuthEmailTokenSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(email=email, password=password)

            if user:
                if not user.is_active:
                    msg = _('User account is disabled.')
                    raise exceptions.ValidationError(msg)
            else:
                msg = _('Unable to log in with provided credentials.')
                raise exceptions.ValidationError(msg)
        else:
            msg = _('Must include "email" and "password"')
            raise exceptions.ValidationError(msg)

        attrs['user'] = user
        return attrs


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = (
            'id', 'email', 'password', 'first_name', 'last_name', 'middle_name',
            'pan_number',
        )
        extra_kwargs = {
            'password': {
                'write_only': True, 
                'min_length': 8,
            },
        }

    def create(self, validated_data):
        customer = Customer.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            middle_name=validated_data.get('middle_name', ''),
            pan_number=validated_data.get('pan_number', ''),
        )
        return customer


class BankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = '__all__'


class CustomerBankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerBankAccount
        read_only_fields = ('customer',)
        fields = '__all__'

    def validate_customer(self, customer) -> Bank:
        """
        Check customer specified in request is same as the authenticated
        customer.
        """
        # Get the authenticated customer
        authenticated_customer = self.context['request'].user

        # Check if it's the same customer
        if customer.id != authenticated_customer.id:
            raise serializers.ValidationError(
                "Cannot create account as another customer"
            )
        return customer

    def validate_bank(self, bank: Bank) -> Bank:
        """
        Check if the bank is unique for the customer
        """
        # Get the authenticated customer
        customer: Customer = self.context['request'].user

        if CustomerBankAccount.objects.filter(
            customer=customer, bank=bank
        ).exists():
            raise serializers.ValidationError(
                f"Customer already has an account in { bank }"
            )
        return bank

    def validate_account_limit(self) -> None:
        """
        Custom validator for checking if maximum accounts limit has been
        reached.
        """
        # Do nothing if updating
        if self.instance: return

        # Get the authenticated customer
        customer: Customer = self.context['request'].user

        num_accounts: int = CustomerBankAccount.objects.filter(
            customer=customer
        ).count()

        if num_accounts >= MAX_ACCOUNTS_PER_CUSTOMER:
            raise serializers.ValidationError(
                "Maximum number of accounts limit reached!"
            )

    def validate(self, attrs: Any) -> Any:
        self.validate_account_limit()
        return super().validate(attrs)

    def update(
        self, instance: CustomerBankAccount, validated_data: Any
    ) -> CustomerBankAccount:
        """
        Prevents update in case the account verification was approved.
        """
        if instance.verification_status == "approved":
            raise exceptions.PermissionDenied(
                detail="Sorry! Cannot update a verified bank account."
            )
        return super().update(instance, validated_data)
