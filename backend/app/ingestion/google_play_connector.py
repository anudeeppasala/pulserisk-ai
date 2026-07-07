import pandas as pd

from app.ingestion.normalized_review import NormalizedReview


def fetch_google_play_reviews_mock() -> pd.DataFrame:
    """
    Mock Google Play connector.

    In real production, this would connect to the official Google Play Developer API
    for apps owned by the company.

    For this portfolio project, we return normalized mock reviews so the ingestion
    architecture is complete without requiring Google Play Console credentials.
    """

    reviews = [
        NormalizedReview(
            source="google_play_mock",
            company="Northstar",
            product_name="Mobile App",
            rating=1,
            comment_text="The Android app keeps freezing after the latest update.",
            comment_date="2026-07-07",
            product_version="9.95.0",
        ),
        NormalizedReview(
            source="google_play_mock",
            company="Northstar",
            product_name="Mobile App",
            rating=1,
            comment_text="I cannot login because the verification code never comes.",
            comment_date="2026-07-07",
            product_version="9.95.0",
        ),
        NormalizedReview(
            source="google_play_mock",
            company="Harbor",
            product_name="Digital Portal",
            rating=1,
            comment_text="The refund page shows an error and billing support does not respond.",
            comment_date="2026-07-07",
            product_version="8.3.0",
        ),
        NormalizedReview(
            source="google_play_mock",
            company="Summit",
            product_name="Customer Portal",
            rating=2,
            comment_text="The app is slow and the dashboard takes forever to load.",
            comment_date="2026-07-07",
            product_version="4.9.0",
        ),
    ]

    return pd.DataFrame([review.to_dict() for review in reviews])