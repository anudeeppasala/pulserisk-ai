"""Data ingestion service for loading reviews from CSV or external sources."""

from pathlib import Path

SAMPLE_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "sample_comments.csv"


def ingest_csv(path: Path = SAMPLE_DATA_PATH) -> int:
    """Load reviews from a CSV file into the database. Returns count ingested."""
    raise NotImplementedError
