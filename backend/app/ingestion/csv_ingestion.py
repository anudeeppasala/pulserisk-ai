from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = {
    "source",
    "company",
    "product_name",
    "rating",
    "comment_text",
    "comment_date",
    "product_version",
}


def load_reviews_from_csv(file_path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(file_path)
    validate_review_dataframe(df)
    return df


def validate_review_dataframe(df: pd.DataFrame) -> list[str]:
    missing_columns = sorted(REQUIRED_COLUMNS - set(df.columns))

    if missing_columns:
        return missing_columns

    return []