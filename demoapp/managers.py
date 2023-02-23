from django.contrib.auth.models import BaseUserManager


class CustomerManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        #
        # The rest_framework.authtoken.serializers.AuthTokenSerializer
        # has hardcoded the username and password fields.
        # 
        # A custom serializer can be made and used instead in the post
        # method of demoapp.views.CustomAuthToken in order to eliminate
        # use of a `username` field in the Customer model.
        #
        if not email:
            raise ValueError('The customer must have an email address')
        email = self.normalize_email(email)
        customer = self.model(email=email, **extra_fields)
        customer.set_password(password)
        customer.save()
        return customer

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)
