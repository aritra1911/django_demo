from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from demoapp.managers import CustomerManager


class Customer(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, blank=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    middle_name = models.CharField(max_length=30, blank=True)
    pan_number = models.CharField(max_length=10, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomerManager()

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'pan_number',]

    def __str__(self):
        return self.get_fullname()

    def get_fullname(self):
        if self.middle_name:
            return f'{self.first_name} {self.middle_name} {self.last_name}'
        return f'{self.first_name} {self.last_name}'


class Bank(models.Model):
    name = models.CharField(max_length=100)
    website = models.URLField()
    number = models.CharField(max_length=20)

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

    account_number = models.CharField(max_length=100)
    ifsc_code = models.CharField(max_length=11)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE)
    cheque_image = models.ImageField(
        upload_to='cheque_images/', null=True, blank=True
    )
    branch_name = models.CharField(max_length=100, blank=True)
    is_cheque_verified = models.BooleanField(default=False)
    name_as_per_bank_record = models.CharField(
        max_length=100, null=True, blank=True
    )
    verification_mode = models.CharField(
        max_length=20, choices=VERIFICATION_MODES, default='manual'
    )
    verification_status = models.CharField(
        max_length=20, choices=VERIFICATION_STATUSES, default='pending'
    )
    account_type = models.CharField(
        max_length=20, choices=ACCOUNT_TYPES, default='savings'
    )

    class Meta:
        verbose_name_plural = 'CustomerBankAccounts'
        unique_together = ('ifsc_code', 'account_number')
        ordering = ('id',)
        constraints = [
            models.UniqueConstraint(
                fields=['account_number', 'ifsc_code'],
                name='unique_bank_account'
            ),
        ]
