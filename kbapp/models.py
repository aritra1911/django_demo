from django.db import models
from typing import Optional, Type, Any, Dict


class BaseModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    modified_by = models.CharField(max_length=250, null=True, blank=True)
    created_by = models.CharField(max_length=250, null=True, blank=True)

    class Meta:
        abstract = True


class AMC(BaseModel):
    name = models.CharField(max_length=200, unique=True)
    amfi_nav_download_dropdown_code = models.IntegerField(
        unique=True, null=True, blank=True
    )
    amc_assets_under_management = models.FloatField(null=True, blank=True)
    description = models.CharField(max_length=200, null=True, blank=True)
    is_being_sold = models.BooleanField(default=False)
    f_amc_code = models.CharField(max_length=3, null=True, blank=True)
    amc_logo = models.CharField(max_length=100)
    amc_website_url = models.CharField(max_length=200, null=True, blank=True)
    scheme_information_document_url = models.CharField(
        max_length=200, null=True, blank=True
    )
    nominee_url = models.CharField(max_length=200, null=True, blank=True)
    expense_ratio_url = models.CharField(max_length=200, null=True, blank=True)
    expense_ratio_url_remarks = models.CharField(
        max_length=200, null=True, blank=True
    )
    last_nav_pull_date_from_amfi = models.DateField(null=True, blank=True)
    rta_amc_code = models.CharField(max_length=64, null=True, blank=True)
    is_isip_available = models.BooleanField(default=False)
    cio = models.CharField(max_length=150, null=True, blank=True)
    ceo = models.CharField(max_length=150, null=True, blank=True)
    management_trustee = models.CharField(max_length=200, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    owner_type = models.CharField(max_length=50, null=True, blank=True)
    address1 = models.CharField(max_length=200, null=True, blank=True)
    address2 = models.CharField(max_length=200, null=True, blank=True)
    address3 = models.CharField(max_length=200, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    pin = models.IntegerField(null=True, blank=True)
    #registrartransferagency = models.ForeignKey(RegistrarTransferAgency,
    #    on_delete=models.SET_NULL, null=True, blank=True
    #)
    amc_aum_date = models.DateTimeField(null=True, blank=True)


class AMCFund(BaseModel):
    RISK_FACTOR_CHOICES = (
        ('LOW', 'LOW'),
        ('MLW', 'MODERATELY LOW'),
        ('MOD', 'MODERATE'),
        ('MDH', 'MODERATELY HIGH'),
        ('HGH', 'HIGH'),
        ('VHG', 'VERY HIGH'),
    )

    amcfund_id = models.AutoField(primary_key=True)
    #amc = models.ForeignKey(AMC, on_delete=models.CASCADE)
    fund_category = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=255)
    description = models.TextField(max_length=1024, default='N.A', blank=True)
    assets_under_management = models.FloatField(
        default=0.0, blank=True, null=True
    )
    assets_under_management_date = models.DateField(null=True, blank=True)
    launch_date = models.DateField(null=True, blank=True)
    is_being_sold = models.BooleanField(null=True, default=True)
    direct_advantage_savings = models.FloatField(
        default=0.0, max_length=20, null=True, blank=True
    )
    smart_savings = models.FloatField(
        default=0.0, max_length=20, null=True, blank=True
    )
    exit_load_codes = models.CharField(null=True, max_length=128, blank=True)
    fund_class = models.CharField(max_length=64, null=True, blank=True)
    risk_factor = models.CharField(
        null=True, choices=RISK_FACTOR_CHOICES, blank=True, max_length=30
    )
    rta_fund_code = models.CharField(max_length=20, unique=True, default='N.A')
    fund_type = models.CharField(max_length=100, null=True, blank=True)
    fund_sub_type = models.CharField(max_length=100, null=True, blank=True)
    fund_type_id = models.SmallIntegerField(null=True, blank=True)
    scheme_information_document_url = models.URLField(blank=True, null=True)
    amcfund_rating = models.PositiveIntegerField(
        default=0, null=True, blank=True
    )
    direct_plan_expense_ratio_in_perc = models.FloatField(
        default=0.0, null=True, blank=True
    )
    regular_plan_expense_ratio_in_perc = models.FloatField(
        null=True, blank=True
    )
    expense_ratio_as_on_date = models.DateField(null=True, blank=True)
    fund_manager = models.CharField(max_length=64, blank=True, null=True)
    fund_objective = models.TextField(max_length=512, blank=True, null=True)
    fund_manager_since = models.DateField(null=True, blank=True)
    turn_over_ratio = models.FloatField(default=0.0, null=True, blank=True)
    turn_over_ratio_date = models.DateField(null=True, blank=True)
    # sd_5yr = models.FloatField(default=0.0, null=True, blank=True)
    # sd_3yr = models.FloatField(default=0.0, null=True, blank=True)

    class Meta:
        pass

    @classmethod
    def update_by_rta_fund_code(cls, **kwargs: Any) -> Optional['AMCFund']:
        rta_fund_code: str = kwargs.pop('rta_fund_code')
        fund: 'AMCFund'
        created: bool

        fund, created = cls.objects.update_or_create(
            rta_fund_code=rta_fund_code,
            defaults=kwargs
        )

        return fund if created else None
