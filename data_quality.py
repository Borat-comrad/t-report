from dataclasses import dataclass


@dataclass(frozen=True)
class SourceRowIssue:
    sheet_name: str
    row_index: int
    column_name: str
    raw_value: str
    reason: str


class RowNormalizationSkipped(Exception):
    def __init__(self, issue: SourceRowIssue) -> None:
        self.issue = issue
        super().__init__(issue.reason)


def format_raw_value(value: object, limit: int = 120) -> str:
    if value is None:
        return ""

    text = str(value).strip()

    if len(text) <= limit:
        return text

    return f"{text[: limit - 3]}..."
