"""
IPCC 2006 Guidelines, Volume 4, Chapter 10 — reference constants for cattle.
All values are global defaults unless otherwise noted.
"""
from typing import Final

# Table 10.2 — Net energy for maintenance coefficient (Cfi), MJ/day/kg^0.75
# Heifer and calf callers should use "steer" per the Table 10.2 footnote for growing animals.
CFI: Final[dict[str, float]] = {
    "bull":  0.386,
    "cow":   0.322,
    "steer": 0.370,
}

# Table 10.3 — Activity coefficient (Ca), dimensionless
CA: Final[dict[str, float]] = {
    "confined":           0.00,
    "pasture_flat_small": 0.17,
    "pasture_hilly":      0.36,
}

# Table 10.4 — NE for lactation per kg milk
# NE_l = milk_yield_kg * (NE_L_BASE + NE_L_FAT * fat_pct)
NE_L_BASE: Final[float] = 1.47  # MJ/kg milk
NE_L_FAT: Final[float] = 0.40   # MJ/kg milk per % fat

# Table 10.6 — Growth coefficient (Cg), dimensionless
CG: Final[dict[str, float]] = {
    "female":   0.8,
    "castrate": 1.0,
    "bull":     1.2,
}

# Table 10.12 — Default methane conversion factor (Ym), % of gross energy
YM_DEFAULTS: Final[dict[str, float]] = {
    "high_quality_pasture": 6.5,
    "feedlot":              3.0,
    "range_low_quality":    6.5,
}

# Physical constant — energy content of CH4 (IPCC 2006, Vol 4, Ch 10, Eq 10.21)
ENERGY_CONTENT_CH4: Final[float] = 55.65  # MJ/kg CH4

DAYS_PER_YEAR: Final[int] = 365
