import unittest
from uuid import UUID

from pydantic import ValidationError

from backend.app.schemas.orders import (
    CollectedOrder,
    DrinkSize,
    NormalizedOrder,
    OrderBatch,
    OrderSubmission,
    Temperature,
)


class OrderSchemaTests(unittest.TestCase):
    def test_submission_creates_trace_id_and_preserves_raw_text(self) -> None:
        submission = OrderSubmission(
            raw_text="민수는 아아, 서연은 뜨아",
        )

        self.assertIsInstance(submission.trace_id, UUID)
        self.assertEqual(submission.raw_text, "민수는 아아, 서연은 뜨아")
        self.assertIsNotNone(submission.created_at.tzinfo)

    def test_normalized_order_defaults_to_tall(self) -> None:
        order = NormalizedOrder(
            person_name="민수",
            menu_name="아메리카노",
            temperature=Temperature.ICE,
            source_text="민수는 아아",
        )

        self.assertEqual(order.size, DrinkSize.TALL)
        self.assertEqual(order.options, ())

    def test_duplicate_people_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValidationError, "duplicate person"):
            OrderBatch(
                orders=(
                    CollectedOrder(person_name="민수", raw_order="아아"),
                    CollectedOrder(person_name="민수", raw_order="뜨아"),
                ),
            )

    def test_blank_names_and_orders_are_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            CollectedOrder(person_name="  ", raw_order="아아")

        with self.assertRaises(ValidationError):
            CollectedOrder(person_name="민수", raw_order="  ")


if __name__ == "__main__":
    unittest.main()
