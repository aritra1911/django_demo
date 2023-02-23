from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from demoapp.models import Customer

class CustomerAdmin(UserAdmin):
    model = Customer
    ordering = ('username',)
    list_display = (
        'username', 'email', 'first_name', 'last_name', 'middle_name',
        'pan_number', 'is_staff', 'is_active',
    )
    search_fields = (
        'username', 'email', 'first_name', 'last_name', 'middle_name',
        'pan_number',
    )

# Register your models here.
admin.site.register(Customer, CustomerAdmin)
