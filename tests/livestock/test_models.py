import pytest
from pydantic import ValidationError

from carbon_farming.livestock.models import (
    ActivityLevel,
    AnimalCategory,
    CattleGroup,
    FeedSystem,
    GrowthClass,
)


def _base_group(**overrides) -> CattleGroup:
    defaults = dict(
        category=AnimalCategory.BEEF_COW,
        body_weight_kg=500.0,
        mature_weight_kg=550.0,
        digestibility_pct=60.0,
        feed_system=FeedSystem.HIGH_QUALITY_PASTURE,
    )
    defaults.update(overrides)
    return CattleGroup(**defaults)


def test_dairy_cow_valid():
    group = CattleGroup(
        category=AnimalCategory.DAIRY_COW,
        body_weight_kg=550.0,
        mature_weight_kg=600.0,
        digestibility_pct=65.0,
        feed_system=FeedSystem.HIGH_QUALITY_PASTURE,
        milk_yield_kg_day=22.0,
        milk_fat_pct=3.8,
    )
    assert group.growth_class == GrowthClass.FEMALE


def test_growth_class_inferred_for_all_categories():
    expected = {
        AnimalCategory.DAIRY_COW: GrowthClass.FEMALE,
        AnimalCategory.BEEF_COW:  GrowthClass.FEMALE,
        AnimalCategory.HEIFER:    GrowthClass.FEMALE,
        AnimalCategory.BULL:      GrowthClass.BULL,
        AnimalCategory.STEER:     GrowthClass.CASTRATE,
        AnimalCategory.CALF:      GrowthClass.CASTRATE,
    }
    for category, expected_class in expected.items():
        group = _base_group(category=category)
        assert group.growth_class == expected_class, f"Failed for {category}"


def test_growth_class_overridable():
    group = _base_group(growth_class=GrowthClass.BULL)
    assert group.growth_class == GrowthClass.BULL


def test_bull_milk_yields_validation_error():
    with pytest.raises(ValidationError, match="milk_yield_kg_day"):
        _base_group(category=AnimalCategory.BULL, milk_yield_kg_day=5.0)


def test_steer_milk_yields_validation_error():
    with pytest.raises(ValidationError, match="milk_yield_kg_day"):
        _base_group(category=AnimalCategory.STEER, milk_yield_kg_day=1.0)


def test_calf_milk_yields_validation_error():
    with pytest.raises(ValidationError, match="milk_yield_kg_day"):
        _base_group(category=AnimalCategory.CALF, milk_yield_kg_day=0.5)


def test_ym_override_accepted():
    group = _base_group(ym_override_pct=4.5)
    assert group.ym_override_pct == 4.5


def test_ym_override_defaults_to_none():
    group = _base_group()
    assert group.ym_override_pct is None


def test_digestibility_below_minimum():
    with pytest.raises(ValidationError):
        _base_group(digestibility_pct=0.5)


def test_digestibility_above_maximum():
    with pytest.raises(ValidationError):
        _base_group(digestibility_pct=101.0)


def test_head_count_must_be_positive():
    with pytest.raises(ValidationError):
        _base_group(head_count=0)


def test_body_weight_must_be_positive():
    with pytest.raises(ValidationError):
        _base_group(body_weight_kg=0.0)


def test_frozen_model_immutable():
    group = _base_group()
    with pytest.raises(Exception):
        group.body_weight_kg = 600.0  # type: ignore[misc]


def test_activity_level_defaults_to_confined():
    group = _base_group()
    assert group.activity_level == ActivityLevel.CONFINED


def test_pregnant_defaults_false():
    group = _base_group()
    assert group.pregnant is False
