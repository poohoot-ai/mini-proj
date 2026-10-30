import unittest
from pathlib import Path

from sqlalchemy import UniqueConstraint

from backend.app.db.models import (
    IncidentModel,
    NormalizedOrderModel,
    RecoveryAttemptModel,
)


class DatabaseModelTests(unittest.TestCase):
    def test_order_person_is_unique_within_request(self) -> None:
        constraints = {
            tuple(constraint.columns.keys())
            for constraint in NormalizedOrderModel.__table__.constraints
            if isinstance(constraint, UniqueConstraint)
        }

        self.assertIn(("request_id", "person_name"), constraints)

    def test_recovery_attempt_number_is_unique_per_incident(self) -> None:
        constraints = {
            tuple(constraint.columns.keys())
            for constraint in RecoveryAttemptModel.__table__.constraints
            if isinstance(constraint, UniqueConstraint)
        }

        self.assertIn(("incident_id", "attempt"), constraints)

    def test_models_do_not_define_secret_columns(self) -> None:
        forbidden = {"password", "api_key", "token", "secret"}
        columns = {
            column.name
            for model in (IncidentModel, NormalizedOrderModel, RecoveryAttemptModel)
            for column in model.__table__.columns
        }

        self.assertTrue(columns.isdisjoint(forbidden))

    def test_initial_migration_contains_required_tables(self) -> None:
        migration = Path("backend/app/db/migrations/0001_initial.sql")
        sql = migration.read_text(encoding="utf-8")

        for table in (
            "menu_items",
            "order_requests",
            "normalized_orders",
            "incidents",
            "recovery_attempts",
        ):
            self.assertIn(f"CREATE TABLE {table}", sql)


if __name__ == "__main__":
    unittest.main()
