"""Risk rules for classifying comments."""
def classify_comment_rule_based(text: str, rating: int | None = None) -> dict:
    text_lower = text.lower()

    category = "General Feedback"
    sub_category = "General Comment"
    risk_type = "Customer Experience Risk"
    owner_team = "Customer Experience Team"
    severity = "Low"
    recommended_action = "Review customer feedback for potential product or service improvements."

    if any(word in text_lower for word in ["login", "password", "face id", "touch id", "sign in", "locked out"]):
        category = "Authentication / Login"
        sub_category = "Login or account access issue"
        risk_type = "Operational Risk"
        owner_team = "Identity & Access Team"
        severity = "High"
        recommended_action = "Investigate authentication and account access failures."

    elif any(word in text_lower for word in ["crash", "freez", "slow", "loading", "bug", "error"]):
        category = "App Reliability"
        sub_category = "Crash or performance issue"
        risk_type = "Digital Reliability Risk"
        owner_team = "Application Platform Team"
        severity = "High"
        recommended_action = "Review recent releases and performance logs for app stability issues."

    elif any(word in text_lower for word in ["fraud", "dispute", "unauthorized", "money missing", "scam", "security"]):
        category = "Fraud / Security Concern"
        sub_category = "Potential fraud, dispute, or security issue"
        risk_type = "Security / Compliance Risk"
        owner_team = "Security Operations Team"
        severity = "Critical"
        recommended_action = "Escalate to security or compliance review queue."

    elif any(word in text_lower for word in ["statement", "document", "tax", "pdf", "download", "upload"]):
        category = "Documents"
        sub_category = "Document access or upload issue"
        risk_type = "Service Operations Risk"
        owner_team = "Document Services Team"
        severity = "Medium"
        recommended_action = "Investigate document access, upload, or download workflow."

    elif any(word in text_lower for word in ["customer service", "support", "hold", "transfer", "representative", "agent"]):
        category = "Customer Support"
        sub_category = "Support experience issue"
        risk_type = "Customer Experience Risk"
        owner_team = "Support Operations Team"
        severity = "Medium"
        recommended_action = "Review support workflow and escalation handling."

    elif any(word in text_lower for word in ["payment", "billing", "charge", "fee", "refund"]):
        category = "Billing / Payments"
        sub_category = "Payment, charge, or refund issue"
        risk_type = "Financial Operations Risk"
        owner_team = "Billing Operations Team"
        severity = "High"
        recommended_action = "Review billing/payment transaction handling."

    if rating is not None and rating <= 2 and severity == "Low":
        severity = "Medium"

    sentiment = "Negative" if rating is not None and rating <= 2 else "Neutral"

    return {
        "category": category,
        "sub_category": sub_category,
        "sentiment": sentiment,
        "severity": severity,
        "risk_type": risk_type,
        "owner_team": owner_team,
        "recommended_action": recommended_action,
        "summary": text[:180],
    }