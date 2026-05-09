from carbon_farming.livestock.constants import (
    CFI, CA, CG, NE_L_BASE, NE_L_FAT, YM_DEFAULTS, ENERGY_CONTENT_CH4, DAYS_PER_YEAR,
)


def test_cfi_contains_expected_keys():
    assert set(CFI.keys()) == {"bull", "cow", "steer"}


def test_cfi_values_in_ipcc_range():
    # IPCC Table 10.2 values are 0.322–0.386
    for v in CFI.values():
        assert 0.3 <= v <= 0.4


def test_ca_keys():
    assert set(CA.keys()) == {"confined", "pasture_flat_small", "pasture_hilly"}


def test_ca_confined_is_zero():
    assert CA["confined"] == 0.0


def test_ca_hilly_greater_than_flat():
    assert CA["pasture_hilly"] > CA["pasture_flat_small"]


def test_cg_keys():
    assert set(CG.keys()) == {"female", "castrate", "bull"}


def test_cg_bull_highest():
    assert CG["bull"] > CG["castrate"] > CG["female"]


def test_ne_l_constants():
    assert NE_L_BASE == 1.47
    assert NE_L_FAT == 0.40


def test_ym_feedlot_below_pasture():
    assert YM_DEFAULTS["feedlot"] < YM_DEFAULTS["high_quality_pasture"]


def test_energy_content_ch4():
    assert ENERGY_CONTENT_CH4 == 55.65


def test_days_per_year():
    assert DAYS_PER_YEAR == 365
