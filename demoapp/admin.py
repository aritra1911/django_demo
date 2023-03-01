from django.contrib import admin
from django.http.request import HttpRequest
from demoapp.models import Customer, Bank, CustomerBankAccount


class ReadOnlyAdmin(admin.ModelAdmin):

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_delete_permission(self, request: HttpRequest, obj=None) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj=None) -> bool:
        return False


class CustomerAdmin(ReadOnlyAdmin):
    ordering = ('email',)
    list_display = (
        'id', 'email', 'first_name', 'last_name', 'middle_name', 'pan_number',
        'is_staff', 'is_active',
    )
    search_fields = (
        'email', 'first_name', 'last_name', 'middle_name', 'pan_number',
    )


class BankAdmin(ReadOnlyAdmin):
    ordering = ('name',)
    list_display = ('id', 'name', 'website', 'number', 'logo',)


class CustomerBankAccountAdmin(ReadOnlyAdmin):
    list_display = (
        'id', 'customer', 'bank', 'account_number', 'ifsc_code', 'is_cheque_verified',
        'account_type', 'is_active',
    )
    list_filter = ('bank', 'is_cheque_verified', 'account_type',)
    search_fields = ('customer__email', 'bank__name', 'account_number',)


admin.site.register(Customer, CustomerAdmin)
admin.site.register(Bank, BankAdmin)
admin.site.register(CustomerBankAccount, CustomerBankAccountAdmin)
