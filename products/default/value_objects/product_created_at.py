from dataclasses import dataclass
from datetime import datetime, UTC


@dataclass(frozen=True)
class CreatedAt:
    value: datetime

    @classmethod
    def now(cls) -> "CreatedAt":
        return cls(datetime.now(UTC))
