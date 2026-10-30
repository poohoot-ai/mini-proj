import unittest
from datetime import datetime
from uuid import uuid4

from pydantic import ValidationError

from backend.app.schemas.incidents import (
    FailureType,
    IncidentRecord,
    IncidentStatus,
    RecoveryAttemptRecord,
    RecoveryResult,
)


class IncidentSchemaTests(unittest.TestCase):
    def test_incident_uses_traceable_defaults(self) -> None:
        incident = IncidentRecord(
            trace_id=uuid4(),
            agent="normalizer",
            failure_type=FailureType.AGENT_TIMEOUT,
            evidence=("response exceeded 10 seconds",),
        )

        self.assertEqual(incident.status, IncidentStatus.OPEN)
        self.assertEqual(incident.attempt, 1)
        self.assertIsNotNone(incident.detected_at.tzinfo)

    def test_incident_rejects_naive_timestamp(self) -> None:
        with self.assertRaisesRegex(ValidationError, "timezone-aware"):
            IncidentRecord(
                trace_id=uuid4(),
                agent="collector",
                failure_type=FailureType.AGENT_FAILURE,
                evidence=("invalid result",),
                detected_at=datetime(2026, 10, 30, 12, 0, 0),
            )

    def test_recovery_attempt_is_limited_to_three(self) -> None:
        with self.assertRaises(ValidationError):
            RecoveryAttemptRecord(
                incident_id=uuid4(),
                attempt=4,
                action="retry",
                result=RecoveryResult.FAILED,
                duration_ms=50,
            )


if __name__ == "__main__":
    unittest.main()
