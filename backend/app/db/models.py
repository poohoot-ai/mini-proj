"""Persistence models for menu, order state, incidents, and recovery attempts."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class MenuItemModel(TimestampMixin, Base):
    __tablename__ = "menu_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    menu_name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    aliases: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    allowed_temperatures: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    allowed_sizes: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    allowed_options: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class OrderRequestModel(TimestampMixin, Base):
    __tablename__ = "order_requests"
    __table_args__ = (
        CheckConstraint("state_version >= 1", name="ck_order_state_version_positive"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    trace_id: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False)
    state_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)


class NormalizedOrderModel(TimestampMixin, Base):
    __tablename__ = "normalized_orders"
    __table_args__ = (
        UniqueConstraint(
            "request_id",
            "person_name",
            name="uq_normalized_order_request_person",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    request_id: Mapped[str] = mapped_column(
        ForeignKey("order_requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    person_name: Mapped[str] = mapped_column(String(80), nullable=False)
    source_text: Mapped[str] = mapped_column(Text, nullable=False)
    menu_name: Mapped[str] = mapped_column(String(120), nullable=False)
    temperature: Mapped[str] = mapped_column(String(20), nullable=False)
    size: Mapped[str] = mapped_column(String(20), nullable=False, default="톨")
    options: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    status: Mapped[str] = mapped_column(String(40), nullable=False)


class IncidentModel(TimestampMixin, Base):
    __tablename__ = "incidents"
    __table_args__ = (
        CheckConstraint("attempt BETWEEN 1 AND 3", name="ck_incident_attempt_range"),
    )

    incident_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    trace_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    agent: Mapped[str] = mapped_column(String(80), nullable=False)
    failure_type: Mapped[str] = mapped_column(String(40), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False)
    evidence: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    attempt: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    requires_human_approval: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class RecoveryAttemptModel(Base):
    __tablename__ = "recovery_attempts"
    __table_args__ = (
        UniqueConstraint(
            "incident_id",
            "attempt",
            name="uq_recovery_incident_attempt",
        ),
        CheckConstraint("attempt BETWEEN 1 AND 3", name="ck_recovery_attempt_range"),
        CheckConstraint("duration_ms >= 0", name="ck_recovery_duration_nonnegative"),
    )

    recovery_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    incident_id: Mapped[str] = mapped_column(
        ForeignKey("incidents.incident_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    attempt: Mapped[int] = mapped_column(Integer, nullable=False)
    action: Mapped[str] = mapped_column(String(120), nullable=False)
    result: Mapped[str] = mapped_column(String(40), nullable=False)
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
