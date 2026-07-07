import pandas as pd

from app.ingestion.normalized_review import NormalizedReview


def fetch_app_store_reviews_mock() -> pd.DataFrame:
    """
    Mock App Store connector.

    In real production, this would connect to App Store Connect API for apps owned
    by the company.

    For this portfolio project, we return normalized mock reviews so the ingestion
    layer is demo-ready without Apple developer credentials.
    """

    reviews = [
        NormalizedReview(
            source="app_store_mock",
            company="Orion",
            product_name="Client Portal",
            rating=1,
            comment_text="The iOS app crashes every time I upload a PDF document.",
            comment_date="2026-07-07",
            product_version="4.8.3",
        ),
        NormalizedReview(
            source="app_store_mock",
            company="Orion",
            product_name="Client Portal",
            rating=2,
            comment_text="Document upload is broken after the latest update.",
            comment_date="2026-07-07",
            product_version="4.8.3",
        ),
        NormalizedReview(
            source="app_store_mock",
            company="Harbor",
            product_name="Mobile App",
            rating=1,
            comment_text="I see suspicious activity and cannot open a dispute in the app.",
            comment_date="2026-07-07",
            product_version="8.3.0",
        ),
        NormalizedReview(
            source="app_store_mock",
            company="Summit",
            product_name="Customer Portal",
            rating=2,
            comment_text="Support transferred me three times and nobody solved my account issue.",
            comment_date="2026-07-07",
            product_version="4.9.0",
        ),
    ]

    return pd.DataFrame([review.to_dict() for review in reviews])