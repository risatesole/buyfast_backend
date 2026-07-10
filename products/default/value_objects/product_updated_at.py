from dataclasses import dataclass
from datetime import datetime, UTC


@dataclass(frozen=True)
class UpdatedAt:
    value: datetime

    @classmethod
    def now(cls) -> "UpdatedAt":
        return cls(datetime.now(UTC))
