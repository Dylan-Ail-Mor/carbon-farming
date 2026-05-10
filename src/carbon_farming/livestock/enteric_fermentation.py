"""
IPCC 2006, Vol 4, Ch 10 — Tier 2 enteric fermentation CH4 for cattle.
"""
from __future__ import annotations

from carbon_farming.livestock.constants import (
    DAYS_PER_YEAR,
    ENERGY_CONTENT_CH4,
    YM_DEFAULTS,
)
from carbon_farming.livestock.models import (
    AnimalCategory,
    CattleGroup,
    EntericCH4Result,
)
from carbon_farming.livestock.net_energy import compute_net_energy

# GWP100 from IPCC AR6 Table 7.SM.7 (fossil CH4 = 29.8, biogenic = 27.9).
# Switch to 25.0 for AR5 or 28.0 for AR6 biogenic if your reporting standard requires it.
GWP100_CH4: float = 27.9

# Maps AnimalCategory to the CFI lookup key in constants.CFI
_CFI_KEY: dict[AnimalCategory, str] = {
    AnimalCategory.DAIRY_COW: "cow",
    AnimalCategory.BEEF_COW:  "cow",
    AnimalCategory.BULL:      "bull",
    AnimalCategory.HEIFER:    "steer",  # Table 10.2 footnote: growing animals use steer Cfi
    AnimalCategory.STEER:     "steer",
    AnimalCategory.CALF:      "steer",
}


def calculate_enteric_ch4(group: CattleGroup) -> EntericCH4Result:
    """
    Calculate annual enteric CH4 emission for one CattleGroup.

    Implements IPCC 2006, Vol 4, Ch 10, Equation 10.21:

        CH4 (kg/head/yr) = (GE × Ym / 100) / 55.65 × 365
    """
    ne = compute_net_energy(
        category_key=_CFI_KEY[group.category],
        body_weight_kg=group.body_weight_kg,
        mature_weight_kg=group.mature_weight_kg,
        weight_gain_kg_day=group.weight_gain_kg_day,
        digestibility_pct=group.digestibility_pct,
        activity_level=group.activity_level,
        growth_class=group.growth_class,
        milk_yield_kg_day=group.milk_yield_kg_day,
        milk_fat_pct=group.milk_fat_pct,
        pregnant=group.pregnant,
    )

    ym = (
        group.ym_override_pct
        if group.ym_override_pct is not None
        else YM_DEFAULTS[group.feed_system.value]
    )

    ch4_per_head_yr = (ne.ge * (ym / 100.0) / ENERGY_CONTENT_CH4) * DAYS_PER_YEAR
    ch4_group_yr = ch4_per_head_yr * group.head_count
    co2e_group_yr = ch4_group_yr * GWP100_CH4

    return EntericCH4Result(
        category=group.category,
        head_count=group.head_count,
        ym_pct=ym,
        net_energy=ne,
        ch4_kg_per_head_yr=ch4_per_head_yr,
        ch4_kg_group_yr=ch4_group_yr,
        ch4_co2e_group_yr=co2e_group_yr,
    )
