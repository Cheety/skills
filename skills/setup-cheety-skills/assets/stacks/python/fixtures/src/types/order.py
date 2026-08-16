from dataclasses import dataclass


@dataclass(frozen=True)
class AuftragData:
    key: str
    amount_cents: int
