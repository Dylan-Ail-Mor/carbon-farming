"""
IPCC 2006, Vol 4, Ch 10 — net energy component calculations for cattle.

All arguments use SI units (kg, MJ, %) to match IPCC notation.
Function names mirror IPCC NE subscripts for equation traceability.
"""
from __future__ import annotations

from carbon_farming.livestock.constants import CA, CFI, CG, NE_L_BASE, NE_L_FAT
from carbon_farming.livestock.models import ActivityLevel, GrowthClass, NetEnergyComponents


def calc_rem(de_pct: float) -> float:
    """
    Ratio of net energy available for maintenance to digestible energy consumed.
    IPCC 2006, Vol 4, Ch 10, Equation 10.14.

    REM = 1.123 - 4.092e-3·DE + 1.126e-5·DE² - 25.4/DE
    """
    de = de_pct
    result = 1.123 - (4.092e-3 * de) + (1.126e-5 * de**2) - (25.4 / de)
    if result <= 0:
        raise ValueError(
            f"REM is non-positive ({result:.4f}) for DE={de_pct}%. "
            "digestibility_pct must be in a physiologically valid range (≥40%)."
        )
    return result


def calc_reg(de_pct: float) -> float:
    """
    Ratio of net energy available for growth to digestible energy consumed.
    IPCC 2006, Vol 4, Ch 10, Equation 10.15.

    REG = 1.164 - 5.160e-3·DE + 1.308e-5·DE² - 37.4/DE
    """
    de = de_pct
    result = 1.164 - (5.160e-3 * de) + (1.308e-5 * de**2) - (37.4 / de)
    if result <= 0:
        raise ValueError(
            f"REG is non-positive ({result:.4f}) for DE={de_pct}%. "
            "digestibility_pct must be in a physiologically valid range (≥40%)."
        )
    return result


def calc_ne_m(category_key: str, body_weight_kg: float) -> float:
    """
    Net energy for maintenance.
    IPCC 2006, Vol 4, Ch 10, Equation 10.3.

    NE_m = Cfi × BW^0.75
    """
    return CFI[category_key] * body_weight_kg**0.75


def calc_ne_a(ne_m: float, activity_level: ActivityLevel) -> float:
    """
    Net energy for activity.
    IPCC 2006, Vol 4, Ch 10, Equation 10.4.

    NE_a = Ca × NE_m
    """
    return CA[activity_level.value] * ne_m


def calc_ne_l(milk_yield_kg_day: float, milk_fat_pct: float) -> float:
    """
    Net energy for lactation.
    IPCC 2006, Vol 4, Ch 10, Equation 10.8.

    NE_l = milk_yield × (1.47 + 0.40 × fat%)
    """
    if milk_yield_kg_day == 0.0:
        return 0.0
    return milk_yield_kg_day * (NE_L_BASE + NE_L_FAT * milk_fat_pct)


def calc_ne_p(ne_m: float, pregnant: bool) -> float:
    """
    Net energy for pregnancy (last two months only).
    IPCC 2006, Vol 4, Ch 10, Equation 10.13.

    NE_p = 0.10 × NE_m  (when pregnant, else 0)

    Callers are responsible for setting pregnant=True only during the last two
    months of gestation, as the IPCC equation specifies.
    """
    return 0.10 * ne_m if pregnant else 0.0


def calc_ne_g(
    body_weight_kg: float,
    mature_weight_kg: float,
    weight_gain_kg_day: float,
    growth_class: GrowthClass,
) -> float:
    """
    Net energy for growth.
    IPCC 2006, Vol 4, Ch 10, Equation 10.6.

    NE_g = 22.02 × (BW / (Cg × BW_mature))^0.75 × BWgain^1.097
    """
    if weight_gain_kg_day == 0.0:
        return 0.0
    cg = CG[growth_class.value]
    ratio = body_weight_kg / (cg * mature_weight_kg)
    return 22.02 * ratio**0.75 * weight_gain_kg_day**1.097


def calc_ge(
    ne_m: float,
    ne_a: float,
    ne_l: float,
    ne_work: float,
    ne_p: float,
    ne_g: float,
    rem: float,
    reg: float,
    de_pct: float,
) -> float:
    """
    Gross energy intake.
    IPCC 2006, Vol 4, Ch 10, Equation 10.16.

    GE = ((NE_m + NE_a + NE_l + NE_work + NE_p) / REM + NE_g / REG) / (DE/100)
    """
    maintenance_sum = ne_m + ne_a + ne_l + ne_work + ne_p
    return (maintenance_sum / rem + ne_g / reg) / (de_pct / 100.0)


def compute_net_energy(
    category_key: str,
    body_weight_kg: float,
    mature_weight_kg: float,
    weight_gain_kg_day: float,
    digestibility_pct: float,
    activity_level: ActivityLevel,
    growth_class: GrowthClass,
    milk_yield_kg_day: float,
    milk_fat_pct: float,
    pregnant: bool,
) -> NetEnergyComponents:
    """Assemble all NE components and GE for one animal group average."""
    rem = calc_rem(digestibility_pct)
    reg = calc_reg(digestibility_pct)
    ne_m = calc_ne_m(category_key, body_weight_kg)
    ne_a = calc_ne_a(ne_m, activity_level)
    ne_l = calc_ne_l(milk_yield_kg_day, milk_fat_pct)
    ne_p = calc_ne_p(ne_m, pregnant)
    ne_g = calc_ne_g(body_weight_kg, mature_weight_kg, weight_gain_kg_day, growth_class)
    ge = calc_ge(ne_m, ne_a, ne_l, 0.0, ne_p, ne_g, rem, reg, digestibility_pct)

    return NetEnergyComponents(
        ne_m=ne_m,
        ne_a=ne_a,
        ne_l=ne_l,
        ne_p=ne_p,
        ne_g=ne_g,
        ne_work=0.0,
        rem=rem,
        reg=reg,
        ge=ge,
    )
