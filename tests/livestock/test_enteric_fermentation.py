import pytest

from carbon_farming.livestock.enteric_fermentation import GWP100_CH4, calculate_enteric_ch4
from carbon_farming.livestock.models import (
    ActivityLevel,
    AnimalCategory,
    CattleGroup,
    FeedSystem,
)


def _feedlot_steer() -> CattleGroup:
    return CattleGroup(
        category=AnimalCategory.STEER,
        body_weight_kg=400.0,
        mature_weight_kg=550.0,
        weight_gain_kg_day=1.0,
        digestibility_pct=75.0,
        feed_system=FeedSystem.FEEDLOT,
        activity_level=ActivityLevel.CONFINED,
    )


def _dairy_cow() -> CattleGroup:
    return CattleGroup(
        category=AnimalCategory.DAIRY_COW,
        body_weight_kg=550.0,
        mature_weight_kg=600.0,
        weight_gain_kg_day=0.0,
        digestibility_pct=65.0,
        feed_system=FeedSystem.HIGH_QUALITY_PASTURE,
        activity_level=ActivityLevel.PASTURE_FLAT_SMALL,
        milk_yield_kg_day=22.0,
        milk_fat_pct=3.8,
    )


def _beef_cow() -> CattleGroup:
    return CattleGroup(
        category=AnimalCategory.BEEF_COW,
        body_weight_kg=500.0,
        mature_weight_kg=550.0,
        digestibility_pct=60.0,
        feed_system=FeedSystem.HIGH_QUALITY_PASTURE,
    )


# ── Range checks from IPCC literature ────────────────────────────────────────

def test_feedlot_steer_ch4_in_expected_range():
    # Feedlot: Ym=3.0% (Table 10.12), DE=75% → lower emissions than pasture cattle.
    # Typical range for feedlot with these parameters: 15–50 kg CH4/head/yr.
    result = calculate_enteric_ch4(_feedlot_steer())
    assert 15.0 <= result.ch4_kg_per_head_yr <= 50.0, (
        f"Feedlot steer CH4 {result.ch4_kg_per_head_yr:.1f} kg/head/yr outside expected 15–50"
    )


def test_dairy_cow_ch4_in_expected_range():
    result = calculate_enteric_ch4(_dairy_cow())
    assert 100.0 <= result.ch4_kg_per_head_yr <= 180.0, (
        f"Dairy cow CH4 {result.ch4_kg_per_head_yr:.1f} kg/head/yr outside expected 100–180"
    )


# ── Result structure ──────────────────────────────────────────────────────────

def test_group_total_is_per_head_times_count():
    group = CattleGroup(
        category=AnimalCategory.BEEF_COW,
        head_count=50,
        body_weight_kg=500.0,
        mature_weight_kg=550.0,
        digestibility_pct=60.0,
        feed_system=FeedSystem.HIGH_QUALITY_PASTURE,
    )
    result = calculate_enteric_ch4(group)
    assert pytest.approx(result.ch4_kg_group_yr) == result.ch4_kg_per_head_yr * 50


def test_co2e_uses_gwp100():
    result = calculate_enteric_ch4(_beef_cow())
    assert pytest.approx(result.ch4_co2e_group_yr) == result.ch4_kg_group_yr * GWP100_CH4


def test_net_energy_components_positive():
    result = calculate_enteric_ch4(_dairy_cow())
    ne = result.net_energy
    assert ne.ne_m > 0
    assert ne.ne_a > 0
    assert ne.ne_l > 0
    assert ne.ge > 0
    assert ne.rem > 0
    assert ne.reg > 0


def test_ne_work_always_zero():
    result = calculate_enteric_ch4(_beef_cow())
    assert result.net_energy.ne_work == 0.0


def test_ym_default_used_when_no_override():
    result = calculate_enteric_ch4(_feedlot_steer())
    assert result.ym_pct == 3.0  # feedlot default


def test_ym_override_changes_result():
    base = _beef_cow()
    override = base.model_copy(update={"ym_override_pct": 3.0})
    r_base = calculate_enteric_ch4(base)
    r_override = calculate_enteric_ch4(override)
    # Default Ym for high_quality_pasture = 6.5%, override = 3.0% → lower emissions
    assert r_override.ch4_kg_per_head_yr < r_base.ch4_kg_per_head_yr


def test_ym_override_reflected_in_result():
    group = _beef_cow().model_copy(update={"ym_override_pct": 4.5})
    result = calculate_enteric_ch4(group)
    assert result.ym_pct == 4.5


# ── Comparative behaviour ─────────────────────────────────────────────────────

def test_feedlot_lower_than_pasture_same_animal():
    pasture = CattleGroup(
        category=AnimalCategory.STEER,
        body_weight_kg=400.0,
        mature_weight_kg=550.0,
        weight_gain_kg_day=1.0,
        digestibility_pct=65.0,
        feed_system=FeedSystem.HIGH_QUALITY_PASTURE,
        activity_level=ActivityLevel.CONFINED,
    )
    feedlot = pasture.model_copy(update={
        "feed_system": FeedSystem.FEEDLOT,
        "digestibility_pct": 75.0,
    })
    # Feedlot has Ym=3.0% vs 6.5% and higher DE — both factors reduce CH4
    r_pasture = calculate_enteric_ch4(pasture)
    r_feedlot = calculate_enteric_ch4(feedlot)
    assert r_feedlot.ch4_kg_per_head_yr < r_pasture.ch4_kg_per_head_yr


def test_pregnant_cow_higher_than_non_pregnant():
    base = _beef_cow()
    pregnant = base.model_copy(update={"pregnant": True})
    r_base = calculate_enteric_ch4(base)
    r_pregnant = calculate_enteric_ch4(pregnant)
    assert r_pregnant.ch4_kg_per_head_yr > r_base.ch4_kg_per_head_yr


def test_category_preserved_in_result():
    result = calculate_enteric_ch4(_dairy_cow())
    assert result.category == AnimalCategory.DAIRY_COW
