"""Incident and recovery attempt contracts."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


class FailureType(StrEnum):
    AGENT_TIMEOUT = "agent_timeout"
    AGENT_FAILURE = "agent_failure"
    DATABASE_FAILURE = "database_failure"
    REPEATED_FAILURE = "repeated_failure"
    HANDOFF_INVALID = "handoff_invalid"
    UNKNOWN = "unknown"


class IncidentStatus(StrEnum):
    OPEN = "open"
    RECOVERING = "recovering"
    VERIFYING = "verifying"
    RESOLVED = "resolved"
    MANUAL_REVIEW = "manual_review"


class RecoveryResult(StrEnum):
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    BLOCKED = "blocked"


class StrictContract(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


def _require_aware(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timestamp must be timezone-aware")
    return value


class IncidentRecord(StrictContract):
    incident_id: UUID = Field(default_factory=uuid4)
    trace_id: UUID
    agent: str
    failure_type: FailureType
    status: IncidentStatus = IncidentStatus.OPEN
    evidence: tuple[str, ...] = Field(min_length=1)
    attempt: int = Field(default=1, ge=1, le=3)
    requires_human_approval: bool = False
    detected_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("agent")
    @classmethod
    def validate_agent(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("agent must not be blank")
        return value

    @field_validator("detected_at")
    @classmethod
    def validate_detected_at(cls, value: datetime) -> datetime:
        return _require_aware(value)


class RecoveryAttemptRecord(StrictContract):
    recovery_id: UUID = Field(default_factory=uuid4)
    incident_id: UUID
    attempt: int = Field(ge=1, le=3)
    action: str
    result: RecoveryResult
    duration_ms: int = Field(ge=0)
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("action")
    @classmethod
    def validate_action(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("action must not be blank")
        return value

    @field_validator("started_at")
    @classmethod
    def validate_started_at(cls, value: datetime) -> datetime:
        return _require_aware(value)
