from weekly_report_models import BuiltWeeklyReport


def build_email_subject(report: BuiltWeeklyReport) -> str:
    report_date_text = report.summary.report_date.strftime("%d.%m.%Y")
    return f"Еженедельный отчет по КП и поставкам — {report_date_text}"


def build_email_body(report: BuiltWeeklyReport) -> str:
    summary = report.summary
    report_date_text = summary.report_date.strftime("%d.%m.%Y")

    key_findings = build_key_findings(report)

    lines = [
        "Добрый день.",
        "",
        f"Направляю еженедельный отчет по КП и поставкам на {report_date_text}.",
        "",
        "Ключевые показатели:",
        f"- критичные КП — {summary.critical_kp_count}",
        f"- КП с просрочкой 1–7 дней — {summary.warning_kp_count}",
        f"- поставки на текущую неделю — {summary.current_week_delivery_count}",
        f"- поставки на следующие 2 недели — {summary.next_two_weeks_delivery_count}",
        f"- менеджеров в зоне контроля — {len(report.manager_summaries)}",
        "",
        "Ключевые наблюдения:",
    ]

    for finding in key_findings:
        lines.append(f"- {finding}")

    lines.extend(
        [
            "",
            "Во вложении:",
            "- краткая сводка в формате DOCX;",
            "- детальная выгрузка в формате XLSX;",
            "- универсальная справка по метрикам отчета в формате DOCX.",
            "",
            "С уважением,",
            "Автоматизированная система отчетности",
        ]
    )

    return "\n".join(lines)


def build_key_findings(report: BuiltWeeklyReport) -> list[str]:
    summary = report.summary
    findings: list[str] = []

    if summary.critical_kp_count > 0:
        findings.append(
            "основная зона внимания — критически просроченные КП, требующие приоритетной проработки"
        )
    else:
        findings.append("критически просроченные КП отсутствуют")

    if summary.warning_kp_count > 0:
        findings.append(
            "в наличии КП с просрочкой 1–7 дней, требуется контроль перехода в критичную зону"
        )
    else:
        findings.append("КП с просрочкой 1–7 дней отсутствуют")

    findings.append(build_delivery_load_finding(report))

    if report.manager_summaries:
        top_manager = report.manager_summaries[0]
        findings.append(
            "наибольшая управленческая нагрузка сейчас у - "
            f"{top_manager.manager_name}: {top_manager.load_status}, {top_manager.bottleneck_reason}"
        )

    if report.manufacturer_bottlenecks:
        top_manufacturer = report.manufacturer_bottlenecks[0]
        findings.append(
            "по косвенным признакам узкое место чаще всего связано с производителем "
            f"{top_manufacturer.group_name}: {top_manufacturer.overdue_kp_count} просроченных КП"
        )

    return findings


def build_delivery_load_finding(report: BuiltWeeklyReport) -> str:
    summary = report.summary

    current_week_count = summary.current_week_delivery_count
    next_two_weeks_count = summary.next_two_weeks_delivery_count

    if current_week_count == 0 and next_two_weeks_count == 0:
        return "в ближайшем горизонте поставки, требующие внимания по отчету, отсутствуют"

    if current_week_count > 0 and next_two_weeks_count == 0:
        return (
            "нагрузка по поставкам сосредоточена на текущей неделе, дальний двухнедельный горизонт пустой"
        )

    if current_week_count == 0 and next_two_weeks_count > 0:
        return (
            "на текущей неделе поставки по отчету отсутствуют, нагрузка смещена на следующий двухнедельный горизонт"
        )

    return (
        "по поставкам есть нагрузка как на текущую неделю, так и на следующий двухнедельный горизонт"
    )
