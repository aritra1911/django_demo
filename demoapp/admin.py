from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from demoapp.models import Customer

class CustomerAdmin(UserAdmin):
    model = Customer
    ordering = ('email',)
    list_display = (
        'email', 'first_name', 'last_name', 'middle_name', 'pan_number',
        'is_staff', 'is_active',
    )
    search_fields = (
        'email', 'first_name', 'last_name', 'middle_name', 'pan_number',
    )

# Register your models here.
admin.site.register(Customer, CustomerAdmin)
