from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, replace

from entity_mapper import DeliveryItem
from kp_analyzer import KpReportItem


@dataclass(frozen=True)
class ManagerSummary:
    manager_name: str
    display_name: str
    ranking_flag: str
    ranking_bucket: str
    overdue_kp_count: int
    critical_kp_count: int
    warning_kp_count: int
    avg_overdue_days: float | None
    max_overdue_days: int | None
    current_week_delivery_count: int
    next_two_weeks_delivery_count: int
    total_delivery_count: int
    workload_score: int
    load_status: str
    efficiency_assessment: str
    bottleneck_reason: str
    delayed_manufacturers: str
    delayed_branches: str


@dataclass(frozen=True)
class BottleneckSummary:
    group_type: str
    group_name: str
    overdue_kp_count: int
    critical_kp_count: int
    warning_kp_count: int
    avg_overdue_days: float | None
    max_overdue_days: int | None
    affected_managers: str
    diagnostic_comment: str


@dataclass(frozen=True)
class ManagementInsights:
    manager_summaries: list[ManagerSummary]
    manufacturer_bottlenecks: list[BottleneckSummary]
    branch_bottlenecks: list[BottleneckSummary]


@dataclass
class _ManagerAccumulator:
    critical_kp_items: list[KpReportItem]
    warning_kp_items: list[KpReportItem]
    current_week_delivery_count: int = 0
    next_two_weeks_delivery_count: int = 0


@dataclass
class _GroupAccumulator:
    critical_kp_items: list[KpReportItem]
    warning_kp_items: list[KpReportItem]


def _normalize_key(value: str) -> str:
    normalized = value.strip()
    if normalized == "":
        return "Не указан"
    return normalized


def _average_overdue(items: list[KpReportItem]) -> float | None:
    if not items:
        return None
    return sum(item.overdue_days for item in items) / len(items)


def _max_overdue(items: list[KpReportItem]) -> int | None:
    if not items:
        return None
    return max(item.overdue_days for item in items)


def _format_top_labels(counter: Counter[str], limit: int = 2) -> str:
    if not counter:
        return ""

    parts: list[str] = []
    for label, count in counter.most_common(limit):
        parts.append(f"{label} ({count})")
    return ", ".join(parts)


def _workload_score(
    critical_count: int,
    warning_count: int,
    current_week_delivery_count: int,
    next_two_weeks_delivery_count: int,
) -> int:
    return (
        critical_count * 5
        + warning_count * 2
        + current_week_delivery_count * 3
        + next_two_weeks_delivery_count
    )


def _load_status(score: int) -> str:
    if score >= 25:
        return "критическая нагрузка"
    if score >= 12:
        return "высокая нагрузка"
    if score >= 5:
        return "умеренная нагрузка"
    return "низкая нагрузка"


def _efficiency_assessment(
    overdue_count: int,
    critical_count: int,
    total_delivery_count: int,
    avg_overdue_days: float | None,
) -> str:
    if overdue_count == 0 and total_delivery_count == 0:
        return "стабильно: просроченных КП и срочных поставок нет"
    if overdue_count == 0 and total_delivery_count > 0:
        return "по КП ситуация под контролем, основная загрузка — поставки"
    if critical_count >= 5 or (avg_overdue_days is not None and avg_overdue_days >= 20):
        return "низкая эффективность по КП: накоплен старый backlog"
    if total_delivery_count >= 4 and overdue_count >= 3:
        return "смешанная перегрузка: одновременно копятся КП и поставки"
    if critical_count > 0:
        return "есть срыв части КП в критическую зону"
    return "есть локальная просрочка, нужен оперативный контроль"


def _bottleneck_reason(
    critical_count: int,
    warning_count: int,
    current_week_delivery_count: int,
    next_two_weeks_delivery_count: int,
    top_manufacturers: str,
    top_branches: str,
) -> str:
    reasons: list[str] = []

    if critical_count >= 3:
        reasons.append("накоплен хвост критически просроченных КП")
    elif warning_count >= 3:
        reasons.append("копится очередь КП с риском перехода в критическую зону")

    if current_week_delivery_count >= 3:
        reasons.append("высокая нагрузка по поставкам на текущую неделю")
    elif next_two_weeks_delivery_count >= 3:
        reasons.append("нагрузка по поставкам смещена на ближайшие две недели")

    if top_manufacturers != "":
        reasons.append(f"просрочка чаще всего связана с производителями: {top_manufacturers}")

    if top_branches != "":
        reasons.append(f"задержки концентрируются по филиалам: {top_branches}")

    if not reasons:
        return "явных узких мест по доступным полям не выявлено"

    return "; ".join(reasons)


def _apply_manager_flags(sorted_items: list[ManagerSummary]) -> list[ManagerSummary]:
    flagged_items: list[ManagerSummary] = []

    for index, item in enumerate(sorted_items):
        if index < 3:
            ranking_flag = "🔴"
            ranking_bucket = "топ-3 худших"
        elif index < 6:
            ranking_flag = "🟡"
            ranking_bucket = "следующие 3"
        else:
            ranking_flag = "🟢"
            ranking_bucket = "остальные"

        flagged_items.append(
            replace(
                item,
                ranking_flag=ranking_flag,
                ranking_bucket=ranking_bucket,
                display_name=f"{ranking_flag} {item.manager_name}",
            )
        )

    return flagged_items


def build_manager_summaries(
    critical_kp_items: list[KpReportItem],
    warning_kp_items: list[KpReportItem],
    current_week_delivery_items: list[DeliveryItem],
    next_two_weeks_delivery_items: list[DeliveryItem],
) -> list[ManagerSummary]:
    accumulators: dict[str, _ManagerAccumulator] = {}

    def get_accumulator(name: str) -> _ManagerAccumulator:
        key = _normalize_key(name)
        if key not in accumulators:
            accumulators[key] = _ManagerAccumulator(
                critical_kp_items=[],
                warning_kp_items=[],
            )
        return accumulators[key]

    for item in critical_kp_items:
        get_accumulator(item.employee).critical_kp_items.append(item)

    for item in warning_kp_items:
        get_accumulator(item.employee).warning_kp_items.append(item)

    for item in current_week_delivery_items:
        get_accumulator(item.owner).current_week_delivery_count += 1

    for item in next_two_weeks_delivery_items:
        get_accumulator(item.owner).next_two_weeks_delivery_count += 1

    result: list[ManagerSummary] = []

    for manager_name, accumulator in accumulators.items():
        all_overdue_kp_items = accumulator.critical_kp_items + accumulator.warning_kp_items

        manufacturer_counter = Counter(
            _normalize_key(item.manufacturer)
            for item in all_overdue_kp_items
        )
        branch_counter = Counter(
            _normalize_key(item.branch)
            for item in all_overdue_kp_items
        )

        delayed_manufacturers = _format_top_labels(manufacturer_counter)
        delayed_branches = _format_top_labels(branch_counter)

        critical_count = len(accumulator.critical_kp_items)
        warning_count = len(accumulator.warning_kp_items)
        overdue_count = len(all_overdue_kp_items)
        total_delivery_count = (
            accumulator.current_week_delivery_count + accumulator.next_two_weeks_delivery_count
        )
        avg_overdue_days = _average_overdue(all_overdue_kp_items)
        workload_score = _workload_score(
            critical_count=critical_count,
            warning_count=warning_count,
            current_week_delivery_count=accumulator.current_week_delivery_count,
            next_two_weeks_delivery_count=accumulator.next_two_weeks_delivery_count,
        )

        result.append(
            ManagerSummary(
                manager_name=manager_name,
                display_name=manager_name,
                ranking_flag="",
                ranking_bucket="",
                overdue_kp_count=overdue_count,
                critical_kp_count=critical_count,
                warning_kp_count=warning_count,
                avg_overdue_days=avg_overdue_days,
                max_overdue_days=_max_overdue(all_overdue_kp_items),
                current_week_delivery_count=accumulator.current_week_delivery_count,
                next_two_weeks_delivery_count=accumulator.next_two_weeks_delivery_count,
                total_delivery_count=total_delivery_count,
                workload_score=workload_score,
                load_status=_load_status(workload_score),
                efficiency_assessment=_efficiency_assessment(
                    overdue_count=overdue_count,
                    critical_count=critical_count,
                    total_delivery_count=total_delivery_count,
                    avg_overdue_days=avg_overdue_days,
                ),
                bottleneck_reason=_bottleneck_reason(
                    critical_count=critical_count,
                    warning_count=warning_count,
                    current_week_delivery_count=accumulator.current_week_delivery_count,
                    next_two_weeks_delivery_count=accumulator.next_two_weeks_delivery_count,
                    top_manufacturers=delayed_manufacturers,
                    top_branches=delayed_branches,
                ),
                delayed_manufacturers=delayed_manufacturers,
                delayed_branches=delayed_branches,
            )
        )

    sorted_result = sorted(
        result,
        key=lambda item: (
            -item.workload_score,
            -item.critical_kp_count,
            -item.overdue_kp_count,
            item.manager_name,
        ),
    )

    return _apply_manager_flags(sorted_result)


def _build_group_bottlenecks(
    *,
    group_type: str,
    group_getter,
    critical_kp_items: list[KpReportItem],
    warning_kp_items: list[KpReportItem],
) -> list[BottleneckSummary]:
    accumulators: dict[str, _GroupAccumulator] = {}

    def get_accumulator(group_name: str) -> _GroupAccumulator:
        key = _normalize_key(group_name)
        if key not in accumulators:
            accumulators[key] = _GroupAccumulator(
                critical_kp_items=[],
                warning_kp_items=[],
            )
        return accumulators[key]

    for item in critical_kp_items:
        get_accumulator(group_getter(item)).critical_kp_items.append(item)

    for item in warning_kp_items:
        get_accumulator(group_getter(item)).warning_kp_items.append(item)

    result: list[BottleneckSummary] = []

    for group_name, accumulator in accumulators.items():
        all_items = accumulator.critical_kp_items + accumulator.warning_kp_items
        manager_counter = Counter(_normalize_key(item.employee) for item in all_items)
        affected_managers = _format_top_labels(manager_counter, limit=3)
        critical_count = len(accumulator.critical_kp_items)
        warning_count = len(accumulator.warning_kp_items)
        overdue_count = len(all_items)
        avg_overdue_days = _average_overdue(all_items)
        max_overdue_days = _max_overdue(all_items)

        if critical_count >= 3:
            diagnostic_comment = "устойчивое узкое место: накоплена критическая просрочка"
        elif avg_overdue_days is not None and avg_overdue_days >= 10:
            diagnostic_comment = "задержка носит затяжной характер, требуется разбор процесса"
        else:
            diagnostic_comment = "зона повышенного контроля"

        result.append(
            BottleneckSummary(
                group_type=group_type,
                group_name=group_name,
                overdue_kp_count=overdue_count,
                critical_kp_count=critical_count,
                warning_kp_count=warning_count,
                avg_overdue_days=avg_overdue_days,
                max_overdue_days=max_overdue_days,
                affected_managers=affected_managers,
                diagnostic_comment=diagnostic_comment,
            )
        )

    return sorted(
        result,
        key=lambda item: (
            -item.critical_kp_count,
            -item.overdue_kp_count,
            -(item.avg_overdue_days or 0),
            item.group_name,
        ),
    )


def build_management_insights(
    critical_kp_items: list[KpReportItem],
    warning_kp_items: list[KpReportItem],
    current_week_delivery_items: list[DeliveryItem],
    next_two_weeks_delivery_items: list[DeliveryItem],
) -> ManagementInsights:
    return ManagementInsights(
        manager_summaries=build_manager_summaries(
            critical_kp_items=critical_kp_items,
            warning_kp_items=warning_kp_items,
            current_week_delivery_items=current_week_delivery_items,
            next_two_weeks_delivery_items=next_two_weeks_delivery_items,
        ),
        manufacturer_bottlenecks=_build_group_bottlenecks(
            group_type="Производитель",
            group_getter=lambda item: item.manufacturer,
            critical_kp_items=critical_kp_items,
            warning_kp_items=warning_kp_items,
        ),
        branch_bottlenecks=_build_group_bottlenecks(
            group_type="Филиал",
            group_getter=lambda item: item.branch,
            critical_kp_items=critical_kp_items,
            warning_kp_items=warning_kp_items,
        ),
    )
