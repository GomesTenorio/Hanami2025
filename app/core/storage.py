from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import pandas as pd


@dataclass
class DatasetState:
    df: pd.DataFrame
    filename: str
    uploaded_at: datetime


CURRENT_DATASET: DatasetState | None = None


def set_dataset(df: pd.DataFrame, filename: str) -> None:
    global CURRENT_DATASET
    CURRENT_DATASET = DatasetState(
        df=df,
        filename=filename,
        uploaded_at=datetime.now(timezone.utc),
    )

