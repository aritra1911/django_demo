from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from rest_framework import exceptions, serializers
from demoapp.models import Customer, Bank, CustomerBankAccount
from typing import Any


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
        fields = '__all__'

    def validate(self, attrs: Any) -> Any:
        """
        Manually trigger the clean() method of CustomerBankAccount model
        instance to check if the custom validation is passed.
        """
        instance = CustomerBankAccount(**attrs)
        try:
            instance.clean()
        # Note that this raises Django's ValidationError Exception
        except ValidationError as e:
            raise serializers.ValidationError(e.args[0])
        return super().validate(attrs)
