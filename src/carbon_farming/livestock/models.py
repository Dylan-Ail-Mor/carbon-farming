from __future__ import annotations

from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, Field, model_validator


class AnimalCategory(StrEnum):
    DAIRY_COW = "dairy_cow"
    BEEF_COW = "beef_cow"
    BULL = "bull"
    HEIFER = "heifer"
    STEER = "steer"
    CALF = "calf"


class ActivityLevel(StrEnum):
    CONFINED = "confined"
    PASTURE_FLAT_SMALL = "pasture_flat_small"
    PASTURE_HILLY = "pasture_hilly"


class GrowthClass(StrEnum):
    """Maps to Table 10.6 Cg values."""
    FEMALE = "female"
    CASTRATE = "castrate"
    BULL = "bull"


class FeedSystem(StrEnum):
    """Maps to Table 10.12 Ym defaults."""
    HIGH_QUALITY_PASTURE = "high_quality_pasture"
    FEEDLOT = "feedlot"
    RANGE_LOW_QUALITY = "range_low_quality"


PositiveFloat = Annotated[float, Field(gt=0)]
NonNegativeFloat = Annotated[float, Field(ge=0)]

_GROWTH_CLASS_BY_CATEGORY: dict[AnimalCategory, GrowthClass] = {
    AnimalCategory.DAIRY_COW: GrowthClass.FEMALE,
    AnimalCategory.BEEF_COW:  GrowthClass.FEMALE,
    AnimalCategory.HEIFER:    GrowthClass.FEMALE,
    AnimalCategory.BULL:      GrowthClass.BULL,
    AnimalCategory.STEER:     GrowthClass.CASTRATE,
    AnimalCategory.CALF:      GrowthClass.CASTRATE,
}

_NON_LACTATING_CATEGORIES = {AnimalCategory.BULL, AnimalCategory.STEER, AnimalCategory.CALF}


class CattleGroup(BaseModel):
    """
    All inputs needed to calculate Tier 2 enteric CH4 for one animal group.
    One instance represents the average individual; multiply per-head results by head_count.
    """
    model_config = {"frozen": True}

    category: AnimalCategory
    head_count: Annotated[int, Field(gt=0)] = 1

    body_weight_kg: PositiveFloat
    mature_weight_kg: PositiveFloat
    weight_gain_kg_day: NonNegativeFloat = 0.0

    digestibility_pct: Annotated[float, Field(ge=1.0, le=100.0)]
    feed_system: FeedSystem
    ym_override_pct: Annotated[float | None, Field(ge=0.0, le=100.0)] = None

    activity_level: ActivityLevel = ActivityLevel.CONFINED

    milk_yield_kg_day: NonNegativeFloat = 0.0
    milk_fat_pct: NonNegativeFloat = 0.0

    pregnant: bool = False

    # Inferred from category by default; overridable for edge cases.
    growth_class: GrowthClass | None = None

    @model_validator(mode="after")
    def _infer_growth_class(self) -> CattleGroup:
        if self.growth_class is None:
            object.__setattr__(self, "growth_class", _GROWTH_CLASS_BY_CATEGORY[self.category])
        return self

    @model_validator(mode="after")
    def _lactation_requires_cow(self) -> CattleGroup:
        if self.category in _NON_LACTATING_CATEGORIES and self.milk_yield_kg_day > 0:
            raise ValueError(
                f"milk_yield_kg_day must be 0 for category {self.category!r}"
            )
        return self


class NetEnergyComponents(BaseModel):
    """Intermediate NE breakdown for audit / MRV transparency. All values MJ/day."""
    model_config = {"frozen": True}

    ne_m: float
    ne_a: float
    ne_l: float
    ne_p: float
    ne_g: float
    ne_work: float
    rem: float
    reg: float
    ge: float


class EntericCH4Result(BaseModel):
    model_config = {"frozen": True}

    category: AnimalCategory
    head_count: int
    ym_pct: float
    net_energy: NetEnergyComponents
    ch4_kg_per_head_yr: float
    ch4_kg_group_yr: float
    ch4_co2e_group_yr: float
