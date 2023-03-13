from django.db import models
from datetime import datetime
from typing import Optional, Any, Tuple


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
    def create_or_update_by_rta_fund_code(cls, **kwargs) -> Tuple['AMCFund', bool]:
        rta_fund_code: str = kwargs.pop('rta_fund_code')
        fund: 'AMCFund'
        created: bool

        fund, created = cls.objects.update_or_create(rta_fund_code=rta_fund_code, defaults=kwargs)

        return fund, created


class AMCScheme(BaseModel):
    SCHEME_TYPE = (
        ('OE', 'Open Ended'),
        ('CE', 'Closed Ended'),
        ('IN', 'Interval Schemes'),
    )
    PLAN_TYPE = (
        ('DIR', 'Direct Plan'),
        ('REG', 'Regular Plan'),
        ('RET', 'Retail Plan'),
        ('INST', 'Institutional Plan'),
        ('SINST', 'Super Institutional Plan')
    )
    PLAN_OPT = (
        ('GR', 'Growth'),
        ('DIV', 'Dividend'),
        ('BO', 'Bonus'),
        ('DDIV', 'Daily Dividend'),
        ('WDIV', 'Weekly Dividend'),
        ('MDIV', 'Monthly Dividend'),
        ('FDIV', 'Fortnightly Dividend'),
        ('QDIV', 'Querterly Dividend'),
        ('HDIV', 'Half Yearly Dividend'),
        ('ADIV', 'Annual Dividend'),
    )
    DIV_OPT = (
        ('PAYOUT', 'Dividend Payout Option'),
        ('REINV', 'Dividend Reinvestment Option'),
        ('BOTH', 'Supports both Payout and Reinvestment the options'),
        ('NA', 'Not Applicable (In case of Growth / Bonus Plans)'),
    )
    SIP_ALLOWED_CHOICE = (('Y', 'Yes'), ('N', 'No'))
    SWP_ALLOWED_CHOICE = (('Y', 'Yes'), ('N', 'No'))
    STP_ALLOWED_CHOICE = (('Y', 'Yes'), ('N', 'No'))
    SWITCH_ALLOWED_CHOICE = (('Y', 'Yes'), ('N', 'No'))
    DEMAT_ALLOWED = (('Y', 'Yes'), ('N', 'No'))
    NFO_CHOICES = (('Y', 'Yes'), ('N', 'No'))

    amcfund = models.ForeignKey(AMCFund, on_delete=models.CASCADE)
    amcfundscheme_id = models.AutoField(primary_key=True)
    regular_scheme_mapping = models.ForeignKey("self", blank=True, null=True, related_name="mapped_regular_scheme",
                                               on_delete=models.PROTECT)
    compare_with_regular_scheme = models.ForeignKey("self", blank=True, null=True, related_name="regular_scheme",
                                                    on_delete=models.PROTECT)
    compare_with_direct_scheme = models.ForeignKey("self", blank=True, null=True, related_name="direct_scheme",
                                                   on_delete=models.PROTECT)

    # Data from Kfin Scheme master.
    is_default_scheme_for_amc_fund = models.BooleanField(null=True, )
    name = models.CharField(default='', max_length=200, unique=True, verbose_name='Full Scheme Name')
    amfi_scheme_code = models.IntegerField(default=0, blank=True, null=True)
    isin_div_or_growth_code = models.CharField(max_length=24, blank=True, null=True)
    isin_div_reinvestment_code = models.CharField(max_length=24, blank=True, null=True)
    is_being_sold = models.BooleanField(null=True, default=False)
    is_direct_fund = models.BooleanField(null=True, default=False)
    is_regular_fund = models.BooleanField(null=True, default=False)
    is_growth_fund = models.BooleanField(null=True, default=False)
    is_div_payout_fund = models.BooleanField(null=True, default=False)
    is_div_reinvestment_fund = models.BooleanField(null=True, default=False)
    rta_sip_flag = models.CharField(max_length=1, choices=SIP_ALLOWED_CHOICE, default='N')
    rta_stp_flag = models.CharField(max_length=1, choices=STP_ALLOWED_CHOICE, default='N')
    rta_swp_flag = models.CharField(max_length=1, choices=SWP_ALLOWED_CHOICE, default='N')
    rta_switch_flag = models.CharField(max_length=1, choices=SWITCH_ALLOWED_CHOICE, default='N')
    f_amc_scheme_code = models.CharField(max_length=5, blank=False, null=False, default='XXXXX')
    rta_unique_no = models.CharField(max_length=20, null=True, blank=True)
    rta_scheme_code = models.CharField(max_length=30,null=True,blank=True, unique=True)
    rta_rta_scheme_code = models.CharField(max_length=20, null=True, blank=True)
    rta_amc_scheme_code = models.CharField(max_length=20, null=True, blank=True)
    rta_isin = models.CharField(max_length=15, null=True, blank=True)
    rta_amc_code = models.CharField(max_length=200, null=True, blank=True)
    rta_scheme_type = models.CharField(max_length=25, null=True, blank=True)
    rta_scheme_plan = models.CharField(max_length=25, null=True, blank=True)
    rta_scheme_name = models.CharField(max_length=500, null=True, blank=True)
    rta_agent_code = models.CharField(max_length=10, default='KARVY')
    rta_scheme_active_flag = models.CharField(max_length=1, null=True, blank=True)
    rta_settlement_type = models.CharField(max_length=20, null=True, blank=True)
    dont_override_exit_load_text_flag = models.BooleanField(default=False)
    rta_lock_in_period_flag = models.CharField(max_length=6, null=True, blank=True)
    rta_lock_in_period = models.CharField(max_length=15, null=True, blank=True)
    rta_channel_partner_code = models.CharField(max_length=30, null=True, blank=True)
    launch_date = models.DateField(null=True, blank=True)
    returns_from_launch = models.FloatField(null=True, blank=True)
    rta_plan_code = models.CharField(max_length=20, null=True, blank=True)
    rta_option_code = models.CharField(max_length=20, null=True, blank=True)

    # Fields related to NFO
    is_nfo = models.CharField(max_length=1, choices=NFO_CHOICES, null=True, blank=True)
    nfo_face_value = models.IntegerField(default=0)
    nfo_start_date = models.DateField(null=True, blank=True)
    nfo_end_date = models.DateField(default=datetime.date(datetime(2099, 1, 1)))
    nfo_reopening_date = models.DateField(blank=True, null=True)

    # Fields related to Purchase.
    rta_purchase_allowed = models.CharField(max_length=2, null=True, blank=True)
    rta_purchase_transaction_code = models.CharField(max_length=20, null=True, blank=True)
    rta_minimum_purchase_amount = models.IntegerField(null=True, blank=True)
    rta_additional_purchase_amount_multiple = models.FloatField(max_length=20, null=True, blank=True)
    rta_maximum_purchase_amount = models.IntegerField(default=9999999)  # Refer BFDLMFAMCP-53
    rta_purchase_amount_multiplier = models.IntegerField(default=1)  # Refer BFDLMFAMCP-53
    rta_purchase_cutoff_time = models.TimeField(null=True, blank=True)

    # Fields related to redemption.
    rta_redemption_allowed = models.CharField(max_length=2, null=True, blank=True)
    rta_redemption_transaction_mode = models.CharField(max_length=2, default='DP')
    rta_minimum_redemption_qty = models.FloatField(max_length=20, default=0.001)  # Refer BFDLMFAMCP-53
    rta_redemption_qty_multiplier = models.FloatField(max_length=15, default=0.001)  # Refer BFDLMFAMCP-53
    rta_maximum_redemption_qty = models.IntegerField(default=9999999)  # Refer BFDLMFAMCP-53
    rta_redemption_amount_minimum = models.FloatField(max_length=20, null=True, blank=True)
    rta_redemption_amount_maximum = models.FloatField(max_length=20, default=9999999)  # Refer BFDLMFAMCP-53
    rta_redemption_amount_multiple = models.FloatField(max_length=20, default=0.001)  # Refer BFDLMFAMCP-53
    rta_redemption_cutoff_time = models.TimeField(null=True, blank=True)

    # Data From Kfin SIP Master
    rta_sip_transaction_mode = models.CharField(max_length=2, default='DP')
    rta_sip_installment_gap = models.IntegerField(default=0)
    rta_sip_status = models.SmallIntegerField(null=True, blank=True)
    rta_sip_frequency = models.CharField(max_length=256, null=True, blank=True)
    # Single Scheme can have multiple frequency.
    # max frequency(daily, weekly, fortnightly, monthly, quarterly, semi_annually, annually)

    # SIP Date (daily, weekly, fortnightly, monthly, quarterly, semi_annually, annually)
    rta_sip_daily_dates = models.CharField(max_length=256, null=True, blank=True)
    rta_sip_weekly_dates = models.CharField(max_length=256, null=True, blank=True)
    rta_sip_fortnightly_dates = models.CharField(max_length=256, null=True, blank=True)
    rta_sip_monthly_dates = models.CharField(max_length=256, null=True, blank=True)
    rta_sip_quarterly_dates = models.CharField(max_length=256, null=True, blank=True)
    rta_sip_semi_annually_dates = models.CharField(max_length=256, null=True, blank=True)
    rta_sip_annually_dates = models.CharField(max_length=256, null=True, blank=True)

    # SIP Min Gap (daily, weekly, fortnightly, monthly, quarterly, semi_annually, annually)
    rta_sip_daily_minimum_gap = models.IntegerField(null=True, blank=True)
    rta_sip_weekly_minimum_gap = models.IntegerField(null=True, blank=True)
    rta_sip_fortnightly_minimum_gap = models.IntegerField(null=True, blank=True)
    rta_sip_monthly_minimum_gap = models.IntegerField(null=True, blank=True)
    rta_sip_quarterly_minimum_gap = models.IntegerField(null=True, blank=True)
    rta_sip_semi_annually_minimum_gap = models.IntegerField(null=True, blank=True)
    rta_sip_annually_minimum_gap = models.IntegerField(null=True, blank=True)

    # SIP Max Gap (daily, weekly, fortnightly, monthly, quarterly, semi_annually, annually)
    rta_sip_daily_maximum_gap = models.IntegerField(null=True, blank=True)
    rta_sip_weekly_maximum_gap = models.IntegerField(null=True, blank=True)
    rta_sip_fortnightly_maximum_gap = models.IntegerField(null=True, blank=True)
    rta_sip_monthly_maximum_gap = models.IntegerField(null=True, blank=True)
    rta_sip_quarterly_maximum_gap = models.IntegerField(null=True, blank=True)
    rta_sip_semi_annually_maximum_gap = models.IntegerField(null=True, blank=True)
    rta_sip_annually_maximum_gap = models.IntegerField(null=True, blank=True)

    # SIP Min installment amount (daily, weekly, fortnightly, monthly, quarterly, semi_annually, annually)
    rta_sip_daily_minimum_installment_amount = models.IntegerField(null=True, blank=True)
    rta_sip_weekly_minimum_installment_amount = models.IntegerField(null=True, blank=True)
    rta_sip_fortnightly_minimum_installment_amount = models.IntegerField(null=True, blank=True)
    rta_sip_monthly_minimum_installment_amount = models.IntegerField(null=True, blank=True)
    rta_sip_quarterly_minimum_installment_amount = models.IntegerField(null=True, blank=True)
    rta_sip_semi_annually_minimum_installment_amount = models.IntegerField(null=True, blank=True)
    rta_sip_annually_minimum_installment_amount = models.IntegerField(null=True, blank=True)
    minimum_investment_amount = models.IntegerField(null=True, blank=True)

    # SIP Max installment amount (daily, weekly, fortnightly, monthly, quarterly, semi_annually, annually)
    rta_sip_daily_maximum_installment_amount = models.IntegerField(null=True, blank=True)
    rta_sip_weekly_maximum_installment_amount = models.IntegerField(null=True, blank=True)
    rta_sip_fortnightly_maximum_installment_amount = models.IntegerField(null=True, blank=True)
    rta_sip_monthly_maximum_installment_amount = models.IntegerField(null=True, blank=True)
    rta_sip_quarterly_maximum_installment_amount = models.IntegerField(null=True, blank=True)
    rta_sip_semi_annually_maximum_installment_amount = models.IntegerField(null=True, blank=True)
    rta_sip_annually_maximum_installment_amount = models.IntegerField(null=True, blank=True)
    rta_sip_maximum_installment_amount = models.IntegerField(null=True, blank=True)

    # SIP Min installment number (daily, weekly, fortnightly, monthly, quarterly, semi_annually, annually)
    rta_sip_daily_minimum_installment_numbers = models.IntegerField(null=True, blank=True)
    rta_sip_weekly_minimum_installment_numbers = models.IntegerField(null=True, blank=True)
    rta_sip_fortnightly_minimum_installment_numbers = models.IntegerField(null=True, blank=True)
    rta_sip_monthly_minimum_installment_numbers = models.IntegerField(null=True, blank=True)
    rta_sip_quarterly_minimum_installment_numbers = models.IntegerField(null=True, blank=True)
    rta_sip_semi_annually_minimum_installment_numbers = models.IntegerField(null=True, blank=True)
    rta_sip_annually_minimum_installment_numbers = models.IntegerField(null=True, blank=True)

    rta_sip_maximum_installment_numbers = models.IntegerField(null=True, blank=True)
    rta_sip_multiplier_amount = models.FloatField(max_length=15, null=True, blank=True)
    rta_sip_pause_flag = models.CharField(max_length=1, null=True, blank=True)
    rta_sip_pause_minimum_numbers = models.IntegerField(null=True, blank=True)
    rta_sip_pause_maximum_numbers = models.IntegerField(null=True, blank=True)

    # Data from Kfin STP Master
    rta_stp_in_minimum_installment_amount = models.IntegerField(null=True, blank=True)
    rta_stp_in_maximum_installment_amount = models.IntegerField(null=True, blank=True)
    rta_stp_out_minimum_installment_amount = models.IntegerField(null=True, blank=True)
    rta_stp_out_maximum_installment_amount = models.IntegerField(null=True, blank=True)
    rta_stp_minimum_installment_units = models.FloatField(max_length=15, null=True, blank=True)
    rta_stp_maximum_installment_units = models.FloatField(max_length=15, null=True, blank=True)
    rta_stp_minimum_installment_number = models.IntegerField(null=True, blank=True)
    rta_stp_maximum_installment_number = models.IntegerField(null=True, blank=True)
    rta_stp_reg_out = models.CharField(max_length=10, null=True, blank=True)    #BFDLMFAMCP-688
    rta_stp_reg_in = models.CharField(max_length=10, null=True, blank=True)     #BFDLMFAMCP-688
    rta_stp_frequency = models.CharField(max_length=16, null=True, blank=True)
    rta_stp_monthly_dates = models.CharField(max_length=256, null=True, blank=True)
    rta_stp_minimum_gap = models.IntegerField(null=True, blank=True)
    rta_stp_maximum_gap = models.IntegerField(null=True, blank=True)
    rta_stp_installment_gap = models.IntegerField(null=True, blank=True)
    rta_swi_allowed = models.CharField(max_length=10, null=True, blank=True)    #BFDLMFAMCP-687
    rta_swo_allowed = models.CharField(max_length=10, null=True, blank=True)    #BFDLMFAMCP-687

    # Below fields will be populated from VR
    expense_ratio_in_perc = models.FloatField(default=0.0, null=True, blank=True)
    assets_under_management = models.FloatField(default=0.0, null=True, blank=True)
    aum_as_on_date = models.DateField(null=True, blank=True)
    rta_exit_load_flag = models.CharField(max_length=10, null=True, blank=True)
    rta_exit_load = models.CharField(max_length=1024, null=True, blank=True)
    rank_ytd = models.IntegerField(null=True, blank=True)
    rank_1day = models.IntegerField(null=True, blank=True)
    rank_1week = models.IntegerField(null=True, blank=True)
    rank_1month = models.IntegerField(null=True, blank=True)
    rank_3month = models.IntegerField(null=True, blank=True)
    rank_6month = models.IntegerField(null=True, blank=True)
    rank_9month = models.IntegerField(null=True, blank=True)
    rank_1year = models.IntegerField(null=True, blank=True)
    rank_2year = models.IntegerField(null=True, blank=True)
    rank_3_yr = models.IntegerField(null=True, blank=True)
    returns_ytd = models.DecimalField(max_digits=24, decimal_places=17, null=True, blank=True)
    returns_1_day = models.DecimalField(max_digits=24, decimal_places=17, null=True, blank=True)
    returns_1_week = models.DecimalField(max_digits=24, decimal_places=17, null=True, blank=True)
    returns_1_mth = models.DecimalField(max_digits=24, decimal_places=17, null=True, blank=True)
    returns_3_mth = models.DecimalField(max_digits=24, decimal_places=17, null=True, blank=True)
    returns_6_mth = models.DecimalField(max_digits=24, decimal_places=17, null=True, blank=True)
    returns_9_mth = models.DecimalField(max_digits=24, decimal_places=17, null=True, blank=True)
    returns_1_yr = models.DecimalField(max_digits=24, decimal_places=17, null=True, blank=True)
    returns_2_yr = models.DecimalField(max_digits=24, decimal_places=17, null=True, blank=True)
    returns_3_yr = models.DecimalField(max_digits=24, decimal_places=17, null=True, blank=True)
    vr_return_rating = models.BigIntegerField(default=0, null=True, blank=True)
    vr_rating_date = models.DateField(null=True, blank=True)
    vr_rating = models.IntegerField(null=True, blank=True)
    vr_risk_rating = models.BigIntegerField(default=0, null=True, blank=True)
    vr_rta_code = models.CharField(max_length=150, blank=True, null=True)
    vr_rta_agent = models.CharField(max_length=150, blank=True, null=True)
    indices_short_name = models.CharField(max_length=150, blank=True, null=True)
    portfolio_turnover_ratio = models.IntegerField(blank=True, null=True)
    investment_objective = models.TextField(max_length=10000, blank=True, null=True)
    stats_standard_deviation = models.DecimalField(max_digits=24, decimal_places=14, null=True, blank=True)
    stats_mean = models.DecimalField(max_digits=24, decimal_places=14, null=True, blank=True)
    stats_sharpe_ratio = models.DecimalField(max_digits=24, decimal_places=14, null=True, blank=True)
    stats_rsquared = models.DecimalField(max_digits=24, decimal_places=14, null=True, blank=True)
    stats_beta = models.DecimalField(max_digits=24, decimal_places=14, null=True, blank=True)
    stats_alpha = models.DecimalField(max_digits=24, decimal_places=14, null=True, blank=True)
    stats_information_ratio = models.DecimalField(max_digits=24, decimal_places=14, null=True, blank=True)
    stats_sortino_ratio = models.DecimalField(max_digits=24, decimal_places=14, null=True, blank=True)
    stats_as_on_date = models.DateField(blank=True, null=True)
    comp_as_on_date = models.DateField(blank=True, null=True)
    comp_equity = models.DecimalField(max_digits=24, decimal_places=8, default=0.0)
    comp_debt = models.DecimalField(max_digits=24, decimal_places=8, default=0.0)
    comp_others = models.DecimalField(max_digits=24, decimal_places=8, default=0.0)
    comp_commodities = models.DecimalField(max_digits=24, decimal_places=8, default=0.0)
    comp_realestate = models.DecimalField(max_digits=24, decimal_places=8, default=0.0)

    # Fields related to Daily NAV. Data From Kfin Daily NAV.
    latest_nav_date = models.DateField(blank=True, null=True)
    latest_nav = models.FloatField(default=0.0, max_length=20)
    nav_day_change = models.FloatField(default=0.0, max_length=20, null=True, blank=True)

    # Fields related to Scheme SIP. Data From Kfin SIP Master.
    rta_sip_minimum_installment_numbers = models.IntegerField(null=True, blank=True)
    rta_sip_minimum_installment_amount = models.IntegerField(null=True, blank=True)
    rta_sip_minimum_gap = models.IntegerField(null=True, blank=True)
    rta_sip_maximum_gap = models.IntegerField(null=True, blank=True)

    rta_scheme_planoptiondesc = models.CharField(max_length=100, blank=True, null=True)
    rta_scheme_option = models.CharField(max_length=50, blank=True, null=True)

    vr_fund_category_id = models.BigIntegerField(null=True, blank=True)
    ret_since_launch = models.DecimalField(max_digits=24, decimal_places=17, null=True, blank=True)

    class Meta:
        indexes = (
            models.Index(fields=['amfi_scheme_code', 'isin_div_or_growth_code']),
            models.Index(fields=['amcfund'], name='kbapp_scheme_amcfund_id_idx'),
            models.Index(fields=['regular_scheme_mapping'], name='kbapp_scheme_reg_map_self_idx'),
            models.Index(fields=['compare_with_regular_scheme'], name='kbapp_scheme_comp_reg_idx'),
            models.Index(fields=['compare_with_direct_scheme'], name='kbapp_scheme_comp_dir_idx'),
            models.Index(fields=['name'], name='kbapp_scheme_name_idx'),
            models.Index(fields=['amfi_scheme_code'], name='kbapp_scheme_amfi_code_idx'),
            models.Index(fields=['isin_div_or_growth_code'], name='kbapp_scheme_div_gr_isin_idx'),
            models.Index(fields=['isin_div_reinvestment_code'], name='kbapp_scheme_rev_isin_idx'),
            models.Index(fields=['is_being_sold'], name='kbapp_scheme_sold_idx'),
            models.Index(fields=['is_direct_fund'], name='kbapp_scheme_dir_idx'),
            models.Index(fields=['is_regular_fund'], name='kbapp_scheme_reg_idx'),
            models.Index(fields=['is_growth_fund'], name='kbapp_scheme_growth_idx'),
            models.Index(fields=['is_div_payout_fund'], name='kbapp_scheme_payout_idx'),
            models.Index(fields=['is_div_reinvestment_fund'], name='kbapp_scheme_rev_idx'),
            models.Index(fields=['rta_sip_flag'], name='kbapp_scheme_is_sip_idx'),
            models.Index(fields=['rta_scheme_code'], name='kbapp_scheme_rta_code_idx'),
            models.Index(fields=['is_nfo'], name='kbapp_scheme_is_nfo_idx'),
            models.Index(fields=['rta_purchase_allowed'], name='kbapp_scheme_rta_pr_idx'),
            models.Index(fields=['latest_nav_date'], name='kbapp_scheme_nav_date_idx'),
            models.Index(fields=['rta_scheme_code'], name='kbapp_scheme_rta_sch_code_idx'),
        )

    def __str__(self) -> str:
        """
        Object representation method.
        :return: Name of the scheme.
        """
        return str(self.name)

    @classmethod
    def create_or_update_by_name(cls, **kwargs) -> Tuple['AMCScheme', bool]:
        name: str = kwargs.pop('name')
        scheme: 'AMCScheme'
        created: bool

        scheme, created = cls.objects.update_or_create(name=name, defaults=kwargs)

        return scheme, created
