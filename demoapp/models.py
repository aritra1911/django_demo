from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from demoapp.managers import CustomerManager
from typing import Optional, Type


class Customer(AbstractBaseUser, PermissionsMixin):
    email: models.EmailField = models.EmailField(unique=True)
    first_name: models.CharField = models.CharField(max_length=30)
    last_name: models.CharField = models.CharField(max_length=30)
    middle_name: models.CharField = models.CharField(
        max_length=30, null=True, blank=True
    )
    pan_number: models.CharField = models.CharField(max_length=10, unique=True)
    is_active: models.BooleanField = models.BooleanField(default=True)
    is_staff: models.BooleanField = models.BooleanField(default=False)

    objects = CustomerManager()

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'pan_number',]

    def __str__(self) -> str:
        return self.get_fullname()

    def get_fullname(self) -> str:
        if self.middle_name:
            return f'{self.first_name} {self.middle_name} {self.last_name}'
        return f'{self.first_name} {self.last_name}'

    @classmethod
    def get_queryset_by_id(
        cls: Type["Customer"],
        id: int
    ) -> Optional[models.QuerySet["Customer"]]:
        queryset = cls.objects.filter(id=id)
        return queryset if queryset else None


class Bank(models.Model):
    name: models.CharField = models.CharField(max_length=100)
    website: models.URLField = models.URLField()
    number: models.CharField = models.CharField(max_length=20)

    # The `logo` field is an image field that stores the bank's logo in
    # a directory called 'bank_logos/' in the 'MEDIA_ROOT' directory
    # specified in Django settings.py
    logo = models.ImageField(upload_to='bank_logos/', null=True, blank=True)

    def __str__(self):
        return self.name


class CustomerBankAccount(models.Model):
    ACCOUNT_TYPES = [
        ('savings', 'Savings'),
        ('current', 'Current'),
        ('credit', 'Credit'),
    ]

    VERIFICATION_MODES = [
        ('manual', 'Manual'),
        ('e-verification', 'E-Verification'),
    ]

    VERIFICATION_STATUSES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    account_number: models.CharField = models.CharField(max_length=100)
    ifsc_code: models.CharField = models.CharField(max_length=11)
    customer: models.ForeignKey = models.ForeignKey(
        Customer, on_delete=models.CASCADE
    )
    bank: models.ForeignKey = models.ForeignKey(Bank, on_delete=models.CASCADE)
    cheque_image = models.ImageField(
        upload_to='cheque_images/', null=True, blank=True
    )
    branch_name: models.CharField = models.CharField(max_length=100)
    is_cheque_verified: models.BooleanField = models.BooleanField(default=False)
    name_as_per_bank_record: models.CharField = models.CharField(max_length=100)
    verification_mode: models.CharField = models.CharField(
        max_length=20, choices=VERIFICATION_MODES, default='manual'
    )
    verification_status: models.CharField = models.CharField(
        max_length=20, choices=VERIFICATION_STATUSES, default='pending'
    )
    account_type: models.CharField = models.CharField(
        max_length=20, choices=ACCOUNT_TYPES, default='savings'
    )
    is_active: models.BooleanField = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'CustomerBankAccounts'
        ordering = ('id',)
        constraints = (
            models.UniqueConstraint(
                fields=('account_number', 'ifsc_code'),
                name='unique_bank_account'
            ),
        )

    @classmethod
    def get_account(
        cls: Type["CustomerBankAccount"],
        ifsc_code: str,
        account_number: str
    ) -> Optional["CustomerBankAccount"]:
        accounts: models.QuerySet[CustomerBankAccount] = cls.objects.filter(
            ifsc_code=ifsc_code,
            account_number=account_number
        )
        if accounts:
            return accounts.get()
        return None

    @classmethod
    def get_accounts_count(
        cls: Type["CustomerBankAccount"],
        customer: Customer
    ) -> int:
        return cls.objects.filter(customer=customer).count()

    @classmethod
    def get_active_account(
        cls: Type["CustomerBankAccount"],
        customer: Customer
    ) -> "CustomerBankAccount":
        return cls.objects.get(customer=customer, is_active=True)

    @classmethod
    def get_existing_account(
        cls: Type["CustomerBankAccount"],
        customer: Customer,
        ifsc_code: str,
        account_number: str
    ) -> Optional["CustomerBankAccount"]:
        existing_accounts: models.QuerySet[CustomerBankAccount] = \
            cls.objects.filter(
                customer=customer,
                ifsc_code=ifsc_code,
                account_number=account_number,
                is_active=False
            )
        return existing_accounts.get() if existing_accounts else None

    @classmethod
    def deactivate_active_account(
        cls: Type["CustomerBankAccount"],
        customer: Customer
    ) -> None:
        cls.objects.filter(
            customer=customer,
            is_active=True
        ).update(is_active=False)

    def activate(self: "CustomerBankAccount") -> None:
        self.is_active = True
        self.save(update_fields=("is_active",))
