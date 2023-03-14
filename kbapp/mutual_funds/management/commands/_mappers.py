import datetime
from kbapp.models import AMCFund
from typing import Dict, Any, Optional


def get_cutoff_time(hhmm: int) -> Optional[datetime.time]:
    if not isinstance(hhmm, int) or len(str(hhmm)) != 4:
        return None

    hh: int = int(str(hhmm)[:2])
    mm: int = int(str(hhmm)[2:])

    return datetime.time(hh, mm)


def fund_mapper(data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        'fund_type': data['category'],
        'fund_sub_type': data['subcategory'],
        'risk_factor': data['risktype'],
        'rta_fund_code': data['scheme'],
        'fund_category': data['category'],
        #'modified_by': BATCH_USER,
    }


def scheme_mapper(data: Dict[str, Any], fund: AMCFund) -> Dict[str, Any]:
    is_direct_fund: bool = 'direct' in data['plandesc'].lower()
    is_growth_fund: bool = 'growth' in data['plandesc'].lower()
    is_regular_fund: bool = 'regular' in data['plandesc'].lower()
    is_div_payout_fund: bool = 'payout' in data['optiondesc'].lower()
    is_div_reinvestment_fund: bool = 'reinvestment' in data['optiondesc'].lower()

    # HACK: I did not write this cursed dict below, but it does seem
    #       like a nice hack.
    planoptiondesc = {
        is_direct_fund and is_growth_fund: 'Direct - Growth',
        is_regular_fund and is_growth_fund: 'Regular - Growth',
        is_direct_fund and is_div_reinvestment_fund: 'Direct – IDCW Reinvestment',
        is_regular_fund and is_div_reinvestment_fund: 'Regular – IDCW Reinvestment',
        is_direct_fund and is_div_payout_fund: 'Direct – IDCW Payout',
        is_regular_fund and is_div_payout_fund: 'Regular – IDCW Payout'
    }

    return {
        'amcfund': fund,
        'name': data['desc'],
        'amfi_scheme_code': data['amficode'] if data['amficode'] else 0,
        'is_active': data['active'] == 'Y',
        'is_being_sold': data['purallow'] == 'Y',
        'is_direct_fund': is_direct_fund,
        'is_regular_fund': is_regular_fund,
        'is_growth_fund': is_growth_fund,
        'is_div_payout_fund': is_div_payout_fund,
        'is_div_reinvestment_fund': is_div_reinvestment_fund,
        'rta_scheme_planoptiondesc': planoptiondesc.get(True, ''),
        'rta_scheme_option': data.get('optiondesc'),
        'rta_sip_flag': data['sipallow'],
        'rta_stp_flag': data['stpoallow'],
        'rta_swp_flag': data['stpiallow'],
        'rta_switch_flag': 'Y' if data['swiallow'] == 'Y' and data['swoallow'] == 'Y' else 'N',
        'rta_stp_reg_in': data['stpiallow'],
        'rta_stp_reg_out': data['stpoallow'],
        'rta_scheme_code': data['schemeid'],
        'rta_rta_scheme_code': data['schemeid'],
        'rta_amc_scheme_code': data['schemeid'],
        'rta_isin': data['isin'],
        'rta_amc_code': data['fundname'],
        'rta_scheme_type': fund.fund_category,
        'rta_scheme_plan': data['plandesc'],
        'rta_scheme_name': data['desc'],
        'rta_scheme_active_flag': data['active'],
        'rta_lock_in_period_flag': 'N',
        'rta_lock_in_period': 0,
        'rta_plan_code': data['plan'],
        'rta_option_code': data['option'],
        'is_nfo': data['nfoidentifier'],
        'nfo_face_value': data['facevalue'],
        'nfo_start_date': datetime.datetime.fromisoformat(data['opendate'][:-1] + '+00.00').date(),
        'nfo_end_date': datetime.datetime.fromisoformat(data['closedate'][:-1] + '+00.00').date(),
        'nfo_reopening_date': datetime.datetime.fromisoformat(data['reopendate'][:-1] + '+00.00').date(),

        # Scheme Purchase Fields
        'rta_purchase_allowed': data['purallow'],
        'rta_minimum_purchase_amount': data['new_minamt'],
        'rta_additional_purchase_amount_multiple': data['add_minamt'],
        'rta_purchase_cutoff_time': get_cutoff_time(data['purcuttime']), # Convert to datetime.time

        # Scheme Redeem Fields
        'rta_redemption_allowed': data['redallow'],
        'rta_redemption_amount_minimum': data['red_minamt'],
        'rta_redemption_cutoff_time': get_cutoff_time(data['redcuttime']),  # Convert to datetime.time
        #'modified_by': BATCH_USER,
        'modified': datetime.datetime.now()
    }
