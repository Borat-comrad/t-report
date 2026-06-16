import unittest
from datetime import date

from entity_mapper import DeliveryItem
from kp_analyzer import KpReportItem
from management_insights import build_management_insights


class ManagementInsightsTests(unittest.TestCase):
    def test_build_management_insights_groups_manager_load_and_bottlenecks(self) -> None:
        critical_items = [
            KpReportItem(
                source_row_index=10,
                request_number="10",
                received_date=date(2026, 3, 1),
                manufacturer="Krones",
                branch="Клин",
                employee="Катя",
                email_subject="КП 1",
                proposal_deadline=date(2026, 3, 10),
                preparation_status="",
                overdue_days=20,
                request_state="Критическая просрочка по КП",
            ),
            KpReportItem(
                source_row_index=11,
                request_number="11",
                received_date=date(2026, 3, 2),
                manufacturer="Krones",
                branch="Клин",
                employee="Катя",
                email_subject="КП 2",
                proposal_deadline=date(2026, 3, 11),
                preparation_status="",
                overdue_days=19,
                request_state="Критическая просрочка по КП",
            ),
            KpReportItem(
                source_row_index=12,
                request_number="12",
                received_date=date(2026, 3, 2),
                manufacturer="Siemens",
                branch="Омск",
                employee="Ира",
                email_subject="КП 3",
                proposal_deadline=date(2026, 3, 25),
                preparation_status="",
                overdue_days=8,
                request_state="Критическая просрочка по КП",
            ),
        ]
        warning_items = [
            KpReportItem(
                source_row_index=13,
                request_number="13",
                received_date=date(2026, 3, 4),
                manufacturer="Krones",
                branch="Клин",
                employee="Катя",
                email_subject="КП 4",
                proposal_deadline=date(2026, 3, 27),
                preparation_status="",
                overdue_days=3,
                request_state="Просрочка по КП 1–7 дней",
            )
        ]
        current_week_deliveries = [
            DeliveryItem(
                source_row_index=20,
                code="A",
                order_received_date=date(2026, 3, 1),
                ro_number="RO-1",
                branch="Клин",
                amount_eur_without_vat=100.0,
                contract="C-1",
                owner="Катя",
                delivery_date=date(2026, 3, 30),
                shipped_actual_date=None,
            ),
            DeliveryItem(
                source_row_index=21,
                code="B",
                order_received_date=date(2026, 3, 1),
                ro_number="RO-2",
                branch="Клин",
                amount_eur_without_vat=50.0,
                contract="C-1",
                owner="Катя",
                delivery_date=date(2026, 3, 31),
                shipped_actual_date=None,
            ),
        ]
        next_two_week_deliveries = [
            DeliveryItem(
                source_row_index=22,
                code="C",
                order_received_date=date(2026, 3, 1),
                ro_number="RO-3",
                branch="Омск",
                amount_eur_without_vat=75.0,
                contract="C-2",
                owner="Ира",
                delivery_date=date(2026, 4, 10),
                shipped_actual_date=None,
            )
        ]

        insights = build_management_insights(
            critical_kp_items=critical_items,
            warning_kp_items=warning_items,
            current_week_delivery_items=current_week_deliveries,
            next_two_weeks_delivery_items=next_two_week_deliveries,
        )

        self.assertEqual(insights.manager_summaries[0].manager_name, "Катя")
        self.assertEqual(insights.manager_summaries[0].display_name, "🔴 Катя")
        self.assertEqual(insights.manager_summaries[0].critical_kp_count, 2)
        self.assertEqual(insights.manager_summaries[0].warning_kp_count, 1)
        self.assertEqual(insights.manager_summaries[0].current_week_delivery_count, 2)
        self.assertIn("Krones", insights.manager_summaries[0].delayed_manufacturers)
        self.assertTrue(insights.manufacturer_bottlenecks)
        self.assertEqual(insights.manufacturer_bottlenecks[0].group_name, "Krones")
        self.assertEqual(insights.branch_bottlenecks[0].group_name, "Клин")


if __name__ == "__main__":
    unittest.main()
