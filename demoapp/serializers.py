from rest_framework import serializers
from demoapp.models import Customer

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = (
            'id', 'username', 'email', 'password', 'first_name', 'last_name',
            'middle_name', 'pan_number',
        )
        extra_kwargs = {
            'password': {
                'write_only': True, 
                'min_length': 8,
            },
        }

    def create(self, validated_data):
        customer = Customer.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            middle_name=validated_data.get('middle_name', ''),
            pan_number=validated_data.get('pan_number', ''),
        )
        return customer
