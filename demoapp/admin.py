from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from demoapp.models import Customer, Bank, CustomerBankAccount


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


class BankAdmin(admin.ModelAdmin):
    list_display = ('name', 'website', 'number', 'logo')


class CustomerBankAccountAdmin(admin.ModelAdmin):
    list_display = (
        'customer', 'bank', 'account_number', 'ifsc_code', 'is_cheque_verified',
        'account_type',
    )
    list_filter = ('bank', 'is_cheque_verified', 'account_type',)
    search_fields = ('customer__email', 'bank__name', 'account_number',)


admin.site.register(Customer, CustomerAdmin)
admin.site.register(Bank, BankAdmin)
admin.site.register(CustomerBankAccount, CustomerBankAccountAdmin)
