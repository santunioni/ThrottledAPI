from typing import Optional


class RateLimitExceeded(Exception):
    def __init__(self, key: str, retry_after: Optional[int] = None):
        self.key = key
        self.retry_after = retry_after
        super().__init__()

    @property
    def detail(self) -> str:
        return f"Rate exceeded for key={self.key}."
