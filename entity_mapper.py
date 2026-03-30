from dataclasses import dataclass
from datetime import date

from delivery_normalizer import NormalizedDeliveryRow
from kp_normalizer import NormalizedKpRow


@dataclass(frozen=True)
class KpItem:
    source_row_index: int
    request_number: str
    received_date: date | None
    manufacturer: str
    branch: str
    employee: str
    email_subject: str
    proposal_deadline: date | None
    preparation_status: str


@dataclass(frozen=True)
class DeliveryItem:
    source_row_index: int
    code: str
    order_received_date: date | None
    ro_number: str
    branch: str
    amount_eur_without_vat: float | None
    contract: str
    owner: str
    delivery_date: date | None
    shipped_actual_date: date | None


def map_kp_rows(normalized_rows: list[NormalizedKpRow]) -> list[KpItem]:
    return [
        KpItem(
            source_row_index=row.source_row_index,
            request_number=row.request_number,
            received_date=row.received_date,
            manufacturer=row.manufacturer,
            branch=row.branch,
            employee=row.employee,
            email_subject=row.email_subject,
            proposal_deadline=row.proposal_deadline,
            preparation_status=row.preparation_status,
        )
        for row in normalized_rows
    ]


def map_delivery_rows(normalized_rows: list[NormalizedDeliveryRow]) -> list[DeliveryItem]:
    return [
        DeliveryItem(
            source_row_index=row.source_row_index,
            code=row.code,
            order_received_date=row.order_received_date,
            ro_number=row.ro_number,
            branch=row.branch,
            amount_eur_without_vat=row.amount_eur_without_vat,
            contract=row.contract,
            owner=row.owner,
            delivery_date=row.delivery_date,
            shipped_actual_date=row.shipped_actual_date,
        )
        for row in normalized_rows
    ]
