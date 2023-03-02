from django.contrib.auth.models import BaseUserManager
from django.core.validators import validate_email


class CustomerManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Creates a Customer User
        """
        if not email:
            raise ValueError('Customer must have an email address')

        if not password:
            raise ValueError('Customer must set a secure password.')

        if not extra_fields.get('first_name'):
            raise ValueError('Customer must mention a first name.')

        if not extra_fields.get('last_name'):
            raise ValueError('Customer must mention their last name.')

        if not extra_fields.get('pan_number'):
            raise ValueError('Customer must mention their PAN number.')

        email = self.normalize_email(email)
        validate_email(email)
        customer = self.model(email=email, **extra_fields)
        customer.set_password(password)
        customer.save()
        return customer

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)
