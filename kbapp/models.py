from django.db import models


class BaseModel(models.Model):
    created: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    modified: models.DateTimeField = models.DateTimeField(auto_now=True)
    is_active: models.BooleanField = models.BooleanField(default=True)
    modified_by: models.CharField = models.CharField(
        max_length=250, null=True, blank=True
    )
    created_by: models.CharField = models.CharField(
        max_length=250, null=True, blank=True
    )

    class Meta:
        abstract = True


class AMC(BaseModel):
    name: models.CharField = models.CharField(max_length=200, unique=True)
    amfi_nav_download_dropdown_code: models.IntegerField = models.IntegerField(
        unique=True, null=True, blank=True
    )
    amc_assets_under_management: models.FloatField = models.FloatField(
        null=True, blank=True
    )
    description: models.CharField = models.CharField(
        max_length=200, null=True, blank=True
    )
    is_being_sold: models.BooleanField = models.BooleanField(default=False)
    f_amc_code: models.CharField = models.CharField(
        max_length=3, null=True, blank=True
    )
    amc_logo: models.CharField = models.CharField(max_length=100)
    amc_website_url: models.CharField = models.CharField(
        max_length=200, null=True, blank=True
    )
    scheme_information_document_url: models.CharField = models.CharField(
        max_length=200, null=True, blank=True
    )
    nominee_url: models.CharField = models.CharField(
        max_length=200, null=True, blank=True
    )
    expense_ratio_url: models.CharField = models.CharField(
        max_length=200, null=True, blank=True
    )
    expense_ratio_url_remarks: models.CharField = models.CharField(
        max_length=200, null=True, blank=True
    )
    last_nav_pull_date_from_amfi: models.DateField = models.DateField(
        null=True, blank=True
    )
    rta_amc_code: models.CharField = models.CharField(
        max_length=64, null=True, blank=True
    )
    is_isip_available: models.BooleanField = models.BooleanField(default=False)
    cio: models.CharField = models.CharField(
        max_length=150, null=True, blank=True
    )
    ceo: models.CharField = models.CharField(
        max_length=150, null=True, blank=True
    )
    management_trustee: models.CharField = models.CharField(
        max_length=200, null=True, blank=True
    )
    start_date: models.DateField = models.DateField(null=True, blank=True)
    phone: models.CharField = models.CharField(
        max_length=50, null=True, blank=True
    )
    email: models.CharField = models.CharField(
        max_length=100, null=True, blank=True
    )
    owner_type: models.CharField = models.CharField(
        max_length=50, null=True, blank=True
    )
    address1: models.CharField = models.CharField(
        max_length=200, null=True, blank=True
    )
    address2: models.CharField = models.CharField(
        max_length=200, null=True, blank=True
    )
    address3: models.CharField = models.CharField(
        max_length=200, null=True, blank=True
    )
    city: models.CharField = models.CharField(
        max_length=100, null=True, blank=True
    )
    pin: models.IntegerField = models.IntegerField(null=True, blank=True)
    #registrartransferagency = models.ForeignKey(RegistrarTransferAgency,
    #    on_delete=models.SET_NULL, null=True, blank=True
    #)
    amc_aum_date: models.DateTimeField = models.DateTimeField(
        null=True, blank=True
    )
