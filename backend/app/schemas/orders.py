"""Order contracts shared by the API, agents, and persistence layer."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class Temperature(StrEnum):
    ICE = "아이스"
    HOT = "따뜻한"


class DrinkSize(StrEnum):
    TALL = "톨"
    GRANDE = "그란데"
    VENTI = "벤티"


class OrderStatus(StrEnum):
    RECEIVED = "received"
    COLLECTED = "collected"
    NEEDS_CLARIFICATION = "needs_clarification"
    NORMALIZED = "normalized"
    VALIDATED = "validated"
    SETTLED = "settled"
    FAILED = "failed"
    MANUAL_REVIEW = "manual_review"


class StrictContract(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class OrderSubmission(StrictContract):
    raw_text: str
    trace_id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("raw_text")
    @classmethod
    def validate_raw_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("raw_text must not be blank")
        return value


class CollectedOrder(StrictContract):
    person_name: str
    raw_order: str

    @field_validator("person_name", "raw_order")
    @classmethod
    def validate_non_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("value must not be blank")
        return value


class OrderBatch(StrictContract):
    trace_id: UUID = Field(default_factory=uuid4)
    state_version: int = Field(default=1, ge=1)
    status: OrderStatus = OrderStatus.COLLECTED
    orders: tuple[CollectedOrder, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def reject_duplicate_people(self) -> OrderBatch:
        names = [order.person_name for order in self.orders]
        if len(names) != len(set(names)):
            raise ValueError("duplicate person names are not allowed")
        return self


class MenuItem(StrictContract):
    menu_name: str
    aliases: tuple[str, ...] = ()
    allowed_temperatures: tuple[Temperature, ...]
    allowed_sizes: tuple[DrinkSize, ...] = (
        DrinkSize.TALL,
        DrinkSize.GRANDE,
        DrinkSize.VENTI,
    )
    allowed_options: tuple[str, ...] = ()
    active: bool = True

    @field_validator("menu_name")
    @classmethod
    def validate_menu_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("menu_name must not be blank")
        return value


class NormalizedOrder(StrictContract):
    person_name: str
    menu_name: str
    temperature: Temperature
    size: DrinkSize = DrinkSize.TALL
    options: tuple[str, ...] = ()
    source_text: str
    status: OrderStatus = OrderStatus.NORMALIZED

    @field_validator("person_name", "menu_name", "source_text")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("required text must not be blank")
        return value

    @field_validator("options")
    @classmethod
    def normalize_options(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        normalized = tuple(option.strip() for option in value if option.strip())
        if len(normalized) != len(set(normalized)):
            raise ValueError("duplicate options are not allowed")
        return normalized
