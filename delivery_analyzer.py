from dataclasses import dataclass

from entity_mapper import DeliveryItem
from report_context_factory import ReportContext


@dataclass(frozen=True)
class DeliveryAnalysisResult:
    current_week_items: list[DeliveryItem]
    next_two_weeks_items: list[DeliveryItem]


def analyze_delivery_items(
    items: list[DeliveryItem],
    context: ReportContext,
) -> DeliveryAnalysisResult:
    current_week_items: list[DeliveryItem] = []
    next_two_weeks_items: list[DeliveryItem] = []

    for item in items:
        if item.delivery_date is None:
            continue

        if context.current_week_start <= item.delivery_date <= context.current_week_end:
            current_week_items.append(item)
            continue

        if (
            context.next_two_weeks_start
            <= item.delivery_date
            <= context.next_two_weeks_end
        ):
            next_two_weeks_items.append(item)

    return DeliveryAnalysisResult(
        current_week_items=current_week_items,
        next_two_weeks_items=next_two_weeks_items,
    )
