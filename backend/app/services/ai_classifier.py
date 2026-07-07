import json
import os
from typing import Optional

from openai import OpenAI

from app.services.risk_rules import classify_comment_rule_based


ALLOWED_CATEGORIES = [
    "Authentication / Login",
    "App Reliability",
    "Customer Support",
    "Documents",
    "Billing / Payments",
    "Fraud / Security Concern",
    "Feature Request",
    "General Feedback",
]

ALLOWED_SENTIMENTS = ["Negative", "Neutral", "Positive"]
ALLOWED_SEVERITIES = ["Low", "Medium", "High", "Critical"]


def classify_comment_ai_ready(
    text: str,
    rating: Optional[int] = None,
    use_ai: bool = False,
) -> dict:
    if not use_ai or not os.getenv("OPENAI_API_KEY"):
        return classify_comment_rule_based(text=text, rating=rating)

    try:
        return _classify_with_openai(text=text, rating=rating)
    except Exception:
        fallback = classify_comment_rule_based(text=text, rating=rating)
        fallback["classification_method"] = "rule_based_fallback_after_ai_error"
        return fallback


def _classify_with_openai(text: str, rating: Optional[int] = None) -> dict:
    client = OpenAI()

    prompt = f"""
You are PulseRisk AI, a Voice-of-Customer risk classification system.

Classify this customer feedback into structured JSON.

Customer rating: {rating}
Customer comment: {text}

Allowed categories:
{ALLOWED_CATEGORIES}

Allowed sentiments:
{ALLOWED_SENTIMENTS}

Allowed severities:
{ALLOWED_SEVERITIES}

Return only valid JSON with this exact shape:
{{
  "category": "",
  "sub_category": "",
  "sentiment": "",
  "severity": "",
  "risk_type": "",
  "owner_team": "",
  "recommended_action": "",
  "summary": ""
}}
"""

    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        messages=[
            {
                "role": "system",
                "content": "Return only valid JSON. Do not include markdown.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.1,
    )

    raw_content = response.choices[0].message.content or "{}"
    parsed = json.loads(raw_content)

    result = {
        "category": parsed.get("category", "General Feedback"),
        "sub_category": parsed.get("sub_category", "General Comment"),
        "sentiment": parsed.get("sentiment", "Neutral"),
        "severity": parsed.get("severity", "Low"),
        "risk_type": parsed.get("risk_type", "Customer Experience Risk"),
        "owner_team": parsed.get("owner_team", "Customer Experience Team"),
        "recommended_action": parsed.get(
            "recommended_action",
            "Review customer feedback for potential product or service improvements.",
        ),
        "summary": parsed.get("summary", text[:180]),
        "classification_method": "openai",
    }

    if result["category"] not in ALLOWED_CATEGORIES:
        result["category"] = "General Feedback"

    if result["sentiment"] not in ALLOWED_SENTIMENTS:
        result["sentiment"] = "Neutral"

    if result["severity"] not in ALLOWED_SEVERITIES:
        result["severity"] = "Low"

    return result