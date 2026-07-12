from dataclasses import dataclass
from abc import ABC

@dataclass
class ProductImages(ABC):
    type: str
    url: str