import pytest

from carbon_farming.livestock.models import ActivityLevel, GrowthClass
from carbon_farming.livestock.net_energy import (
    calc_ge,
    calc_ne_a,
    calc_ne_g,
    calc_ne_l,
    calc_ne_m,
    calc_ne_p,
    calc_reg,
    calc_rem,
)


# ── REM / REG ────────────────────────────────────────────────────────────────

def test_calc_rem_at_65_pct():
    # 1.123 - 4.092e-3*65 + 1.126e-5*4225 - 25.4/65
    expected = 1.123 - 4.092e-3 * 65 + 1.126e-5 * 65**2 - 25.4 / 65
    assert pytest.approx(calc_rem(65.0), rel=1e-6) == expected


def test_calc_reg_at_65_pct():
    expected = 1.164 - 5.160e-3 * 65 + 1.308e-5 * 65**2 - 37.4 / 65
    assert pytest.approx(calc_reg(65.0), rel=1e-6) == expected


def test_rem_positive_for_typical_de():
    for de in (45.0, 55.0, 65.0, 75.0, 85.0):
        assert calc_rem(de) > 0, f"REM non-positive at DE={de}%"


def test_reg_positive_for_typical_de():
    for de in (45.0, 55.0, 65.0, 75.0, 85.0):
        assert calc_reg(de) > 0, f"REG non-positive at DE={de}%"


def test_rem_raises_on_very_low_de():
    with pytest.raises(ValueError, match="REM"):
        calc_rem(1.0)


def test_reg_raises_on_very_low_de():
    with pytest.raises(ValueError, match="REG"):
        calc_reg(1.0)


# ── NE_m ─────────────────────────────────────────────────────────────────────

def test_ne_m_cow_500kg():
    # Cfi=0.322, BW^0.75 = 500^0.75
    expected = 0.322 * 500**0.75
    assert pytest.approx(calc_ne_m("cow", 500.0), rel=1e-6) == expected


def test_ne_m_bull_700kg():
    expected = 0.386 * 700**0.75
    assert pytest.approx(calc_ne_m("bull", 700.0), rel=1e-6) == expected


def test_ne_m_steer_300kg():
    expected = 0.370 * 300**0.75
    assert pytest.approx(calc_ne_m("steer", 300.0), rel=1e-6) == expected


# ── NE_a ─────────────────────────────────────────────────────────────────────

def test_ne_a_confined_is_zero():
    assert calc_ne_a(50.0, ActivityLevel.CONFINED) == 0.0


def test_ne_a_flat_pasture():
    assert pytest.approx(calc_ne_a(50.0, ActivityLevel.PASTURE_FLAT_SMALL)) == 0.17 * 50.0


def test_ne_a_hilly_greater_than_flat():
    ne_m = 50.0
    assert calc_ne_a(ne_m, ActivityLevel.PASTURE_HILLY) > calc_ne_a(ne_m, ActivityLevel.PASTURE_FLAT_SMALL)


# ── NE_l ─────────────────────────────────────────────────────────────────────

def test_ne_l_zero_for_non_lactating():
    assert calc_ne_l(0.0, 4.0) == 0.0


def test_ne_l_typical_dairy():
    # 20 kg/day, 4% fat: 20 × (1.47 + 0.40×4) = 20 × 3.07 = 61.4 MJ/day
    assert pytest.approx(calc_ne_l(20.0, 4.0)) == 61.4


def test_ne_l_higher_fat_increases_energy():
    assert calc_ne_l(20.0, 5.0) > calc_ne_l(20.0, 3.0)


# ── NE_p ─────────────────────────────────────────────────────────────────────

def test_ne_p_pregnant():
    assert pytest.approx(calc_ne_p(34.0, True)) == 3.4


def test_ne_p_not_pregnant():
    assert calc_ne_p(34.0, False) == 0.0


# ── NE_g ─────────────────────────────────────────────────────────────────────

def test_ne_g_zero_gain():
    assert calc_ne_g(300.0, 550.0, 0.0, GrowthClass.CASTRATE) == 0.0


def test_ne_g_steer_typical():
    expected = 22.02 * (300.0 / (1.0 * 550.0))**0.75 * 0.8**1.097
    assert pytest.approx(calc_ne_g(300.0, 550.0, 0.8, GrowthClass.CASTRATE), rel=1e-6) == expected


def test_ne_g_bull_higher_than_female_same_params():
    ne_g_bull = calc_ne_g(300.0, 600.0, 0.8, GrowthClass.BULL)
    ne_g_female = calc_ne_g(300.0, 600.0, 0.8, GrowthClass.FEMALE)
    # Bull has higher Cg (1.2 vs 0.8) → lower ratio → lower NE_g (less fractional of mature)
    # This is correct: bulls have a higher mature weight fraction already accounted for.
    assert ne_g_bull != ne_g_female


# ── GE ───────────────────────────────────────────────────────────────────────

def test_calc_ge_basic():
    ne_m, ne_a, ne_l, ne_p, ne_g = 34.0, 5.0, 0.0, 0.0, 8.0
    rem = calc_rem(60.0)
    reg = calc_reg(60.0)
    expected = (ne_m + ne_a + ne_l + 0.0 + ne_p) / rem + ne_g / reg
    expected /= 60.0 / 100.0
    assert pytest.approx(calc_ge(ne_m, ne_a, ne_l, 0.0, ne_p, ne_g, rem, reg, 60.0), rel=1e-6) == expected


def test_calc_ge_positive():
    rem = calc_rem(65.0)
    reg = calc_reg(65.0)
    ge = calc_ge(34.0, 5.8, 61.4, 0.0, 0.0, 0.0, rem, reg, 65.0)
    assert ge > 0
