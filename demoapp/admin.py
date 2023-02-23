from django.contrib import admin
from demoapp.models import Customer

class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        'username', 'email', 'first_name', 'last_name', 'middle_name',
        'pan_number', 'is_staff', 'is_active',
    )

# Register your models here.
admin.site.register(Customer, CustomerAdmin)
