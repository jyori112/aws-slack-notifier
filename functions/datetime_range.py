from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class DatetimeRange:
    start: datetime
    end: datetime
