from django.contrib.auth.models import BaseUserManager


class CustomerManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        #
        # The rest_framework.authtoken.serializers.AuthTokenSerializer
        # has hardcoded the username and password fields.
        # 
        # A custom serializer can be made and used instead in the post
        # method of demoapp.views.CustomAuthToken in order to eliminate
        # use of a `username` field in the Customer model.
        #
        if not username:
            raise ValueError('The customer must have a username')
        extra_fields['email'] = self.normalize_email(
            extra_fields.get('email', '')
        )
        customer = self.model(username=username, **extra_fields)
        customer.set_password(password)
        customer.save()
        return customer

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, password, **extra_fields)
