from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from django.db.models import QuerySet
from rest_framework import exceptions, serializers
from demo import settings
from demoapp.models import Customer, Bank, CustomerBankAccount
from typing import Any, Dict


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
        read_only_fields = ('id',)
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
        read_only_fields = ('id',)
        fields = '__all__'


class CustomerBankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerBankAccount
        read_only_fields = ('id', 'customer',)
        fields = '__all__'

    def validate_unique_account(
        self, ifsc_code: str, account_number: str
    ) -> None:
        """
        Custom validator to check whether new IFSC code and Account
        Number pair is unique.

        During update operation, the IFSC code and Account Number must
        not have been modified.
        """
        if self.instance:
            instance: CustomerBankAccount = self.instance   # type: ignore
            if ifsc_code != instance.ifsc_code or \
               account_number != instance.account_number:
                raise serializers.ValidationError(
                    "You cannot modify IFSC Code and Account Number for an "
                    "active account."
                )
            return

        if CustomerBankAccount.objects.filter(
            ifsc_code=ifsc_code,
            account_number=account_number
        ):
            raise serializers.ValidationError(
                "Account already exists!"
            )

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

        if num_accounts >= settings.MAX_ACCOUNTS_PER_CUSTOMER:
            raise serializers.ValidationError(
                "Maximum number of accounts limit reached!"
            )

    def validate(self, attrs: Dict[str, Any]) -> Any:
        self.validate_account_limit()
        self.validate_unique_account(
            ifsc_code=attrs['ifsc_code'],
            account_number=attrs['account_number']
        )
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

    def to_representation(self, instance: CustomerBankAccount) -> Any:
        representation: Any = super().to_representation(instance)
        bank: Bank = instance.bank
        logo = bank.logo
        if logo:
            representation['bank_logo'] = settings.MEDIA_ROOT + logo.url
        return representation
