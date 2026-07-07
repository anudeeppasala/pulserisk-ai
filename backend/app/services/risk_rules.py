from typing import Optional


def _contains_any(text: str, keywords: list[str]) -> bool:
    return any(keyword in text for keyword in keywords)


def classify_comment_rule_based(text: str, rating: Optional[int] = None) -> dict:
    """
    Transparent rule-based classifier used as the default V2 fallback.

    V2 supports AI-ready classification, but this rule engine keeps the project
    fully runnable without API keys.
    """

    clean_text = text.strip()
    text_lower = clean_text.lower()

    category = "General Feedback"
    sub_category = "General Comment"
    risk_type = "Customer Experience Risk"
    owner_team = "Customer Experience Team"
    severity = "Low"
    recommended_action = "Review customer feedback for potential product or service improvements."

    if _contains_any(
        text_lower,
        [
            "login",
            "log in",
            "password",
            "face id",
            "touch id",
            "sign in",
            "signin",
            "locked out",
            "verification code",
            "otp",
            "authentication",
            "access my account",
            "reset",
        ],
    ):
        category = "Authentication / Login"
        sub_category = "Login, verification, or account access issue"
        risk_type = "Operational Risk"
        owner_team = "Identity & Access Team"
        severity = "High"
        recommended_action = "Investigate authentication, verification, password reset, and account access failures."

    elif _contains_any(
        text_lower,
        [
            "crash",
            "crashing",
            "freez",
            "slow",
            "loading",
            "bug",
            "error",
            "unknown error",
            "not working",
            "blank screen",
            "stuck",
            "broken",
        ],
    ):
        category = "App Reliability"
        sub_category = "Crash, bug, or performance issue"
        risk_type = "Digital Reliability Risk"
        owner_team = "Application Platform Team"
        severity = "High"
        recommended_action = "Review recent releases, app telemetry, and performance logs for stability issues."

    elif _contains_any(
        text_lower,
        [
            "fraud",
            "dispute",
            "unauthorized",
            "money missing",
            "scam",
            "security",
            "stolen",
            "suspicious",
        ],
    ):
        category = "Fraud / Security Concern"
        sub_category = "Potential fraud, dispute, or security issue"
        risk_type = "Security / Compliance Risk"
        owner_team = "Security Operations Team"
        severity = "Critical"
        recommended_action = "Escalate to security, fraud, or compliance review queue."

    elif _contains_any(
        text_lower,
        [
            "statement",
            "document",
            "tax",
            "pdf",
            "download",
            "upload",
            "file",
            "attachment",
        ],
    ):
        category = "Documents"
        sub_category = "Document access, upload, or download issue"
        risk_type = "Service Operations Risk"
        owner_team = "Document Services Team"
        severity = "Medium"
        recommended_action = "Investigate document access, upload, download, or file-processing workflow."

    elif _contains_any(
        text_lower,
        [
            "customer service",
            "support",
            "hold",
            "transfer",
            "representative",
            "agent",
            "nobody helps",
            "no response",
        ],
    ):
        category = "Customer Support"
        sub_category = "Support experience issue"
        risk_type = "Customer Experience Risk"
        owner_team = "Support Operations Team"
        severity = "Medium"
        recommended_action = "Review support workflow, handoff quality, and escalation handling."

    elif _contains_any(
        text_lower,
        [
            "payment",
            "billing",
            "charge",
            "charged",
            "fee",
            "refund",
            "double charged",
            "transaction",
        ],
    ):
        category = "Billing / Payments"
        sub_category = "Payment, charge, refund, or transaction issue"
        risk_type = "Financial Operations Risk"
        owner_team = "Billing Operations Team"
        severity = "High"
        recommended_action = "Review billing, refund, and payment transaction handling."

    elif _contains_any(
        text_lower,
        [
            "filter",
            "navigation",
            "feature",
            "wish",
            "improve",
            "better",
            "enhancement",
        ],
    ):
        category = "Feature Request"
        sub_category = "Product enhancement request"
        risk_type = "Product Experience Opportunity"
        owner_team = "Product Management Team"
        severity = "Low"
        recommended_action = "Review as product enhancement input for roadmap planning."

    sentiment = detect_sentiment(text_lower=text_lower, rating=rating)

    if rating is not None:
        if rating <= 1 and severity in ["Low", "Medium"]:
            severity = "High"
        elif rating <= 2 and severity == "Low":
            severity = "Medium"

    return {
        "category": category,
        "sub_category": sub_category,
        "sentiment": sentiment,
        "severity": severity,
        "risk_type": risk_type,
        "owner_team": owner_team,
        "recommended_action": recommended_action,
        "summary": clean_text[:180],
        "classification_method": "rule_based",
    }


def detect_sentiment(text_lower: str, rating: Optional[int]) -> str:
    negative_keywords = [
        "bad",
        "terrible",
        "awful",
        "hate",
        "frustrating",
        "angry",
        "worst",
        "broken",
        "not working",
        "cannot",
        "can't",
        "failed",
        "failing",
        "confusing",
        "locked out",
    ]

    positive_keywords = [
        "good",
        "great",
        "excellent",
        "love",
        "helpful",
        "easy",
        "smooth",
        "fast",
    ]

    if rating is not None:
        if rating <= 2:
            return "Negative"
        if rating >= 4:
            return "Positive"

    if _contains_any(text_lower, negative_keywords):
        return "Negative"

    if _contains_any(text_lower, positive_keywords):
        return "Positive"

    return "Neutral"


def get_severity_rank(severity: str) -> int:
    severity_order = {
        "Critical": 4,
        "High": 3,
        "Medium": 2,
        "Low": 1,
    }

    return severity_order.get(severity, 0)