from typing import Optional


class RateLimitExceeded(Exception):
    def __init__(self, key: str, retry_after: Optional[float] = None):
        self.key = key
        self.retry_after = retry_after
        super().__init__()
