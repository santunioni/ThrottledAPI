import time as clock
from dataclasses import dataclass, field
from typing import NamedTuple


@dataclass(frozen=True)
class Hit:
    key: str = field(
        default_factory=str,
        metadata={"description": "The base contribution to the hit key."},
    )
    time: float = field(
        default_factory=clock.time,
        metadata={
            "units": "seconds",
            "description": "time the hit occurred since epoch.",
        },
    )
    cost: int = 1


class Rate(NamedTuple):
    hits: int
    interval: float
