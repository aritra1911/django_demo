from django.contrib.auth.models import BaseUserManager


class CustomerManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
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
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, password, **extra_fields)
