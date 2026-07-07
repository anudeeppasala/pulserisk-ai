from dataclasses import asdict, dataclass
from typing import Optional


@dataclass
class NormalizedReview:
    source: str
    company: str
    product_name: str
    rating: Optional[int]
    comment_text: str
    comment_date: str
    product_version: str

    def to_dict(self) -> dict:
        return asdict(self)