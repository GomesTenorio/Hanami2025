from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import pandas as pd


@dataclass
class InMemoryDataset:
    df: pd.DataFrame
    filename: str
    uploaded_at: datetime


# armazenamento simples em memória (MVP)
CURRENT_DATASET: Optional[InMemoryDataset] = None
