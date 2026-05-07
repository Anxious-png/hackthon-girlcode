"""
Advanced scam detection engine for SilentGuard.
Uses TF-IDF + Naive Bayes when scikit-learn is available,
falls back to a weighted keyword scoring system otherwise.
"""

import re
from typing import Tuple

# ── Scam training data ──────────────────────────────────────────────────────
SCAM_SAMPLES = [
    "You have won a lottery prize of 5 million shillings. Send your pin to claim.",
    "Urgent! Your account will be locked. Click here to unlock now.",
    "Congratulations! You have been selected for a free reward. Send money to verify.",
    "Win a jackpot prize today. Send your mobile money pin to 0700000000.",
    "Free airtime bonus! Claim your reward by sending 1000 to this number.",
    "Your MTN account is suspended. Unlock it by sending your pin urgently.",
    "You have won 10 million in our lottery. Click here to claim your prize.",
    "Send money now to receive your bonus reward. Risk free guaranteed.",
    "Airtel money bonus! Send pin to unlock your free prize today.",
    "Urgent: verify your account or it will be deleted. Send pin immediately.",
    "Congratulations winner! You have won a jackpot. Claim now before it expires.",
    "Free money transfer! Send 500 to receive 5000 back. Limited time offer.",
]

SAFE_SAMPLES = [
    "Your ABSA transaction of UGX 50000 was successful on 22/04/2026.",
    "MTN: Your balance is UGX 12,500. Dial *165# to check.",
    "Dear customer, your electricity bill of 30000 is due on 30th April.",
    "Airtel: You have received UGX 20000 from John. New balance: 35000.",
    "Your OTP for login is 482910. Valid for 5 minutes. Do not share.",
    "ABSA Bank: Your account ending 4521 has been credited with UGX 100000.",
    "Reminder: Your loan repayment of UGX 75000 is due tomorrow.",
    "Your mobile money withdrawal of UGX 10000 was processed successfully.",
    "Thank you for shopping at Nakumatt. Receipt #00234. Total: UGX 45000.",
    "Your internet bundle of 1GB expires in 2 days. Dial *175# to renew.",
]

# ── Weighted keyword scoring ─────────────────────────────────────────────────
HIGH_RISK_KEYWORDS = {
    "pin": 30, "send your pin": 40, "send pin": 40,
    "you have won": 35, "you've won": 35,
    "lottery": 30, "jackpot": 30,
    "claim your prize": 35, "claim now": 25,
    "click here": 20, "click link": 20,
    "unlock your account": 25, "account locked": 20,
    "free money": 30, "send money to receive": 35,
    "risk free": 20, "guaranteed": 15,
    "congratulations winner": 35, "congratulations you have won": 40,
    "urgent": 15, "immediately": 15,
    "verify your account": 20, "account will be deleted": 30,
    "bonus reward": 25, "free reward": 25,
    "win prize": 30, "win a prize": 30,
    "mpesa pin": 40, "airtel money pin": 40,
    "send 500": 20, "send 1000": 20,
}

MEDIUM_RISK_KEYWORDS = {
    "free": 8, "win": 8, "prize": 8, "reward": 8,
    "bonus": 8, "claim": 10, "unlock": 10,
    "limited time": 10, "expires": 5, "offer": 5,
    "selected": 8, "chosen": 8, "lucky": 8,
    "transfer": 5, "send": 5,
}

TRUSTED_SENDERS = [
    "absa", "stanbic", "centenary", "dfcu", "kcb", "equity",
    "mtn", "airtel", "utl", "africell",
    "0800", "256800",
]


def _keyword_score(text: str) -> Tuple[float, list]:
    """Return (score 0-100, detected_keywords list)."""
    lower = text.lower()
    score = 0
    detected = []

    for phrase, weight in HIGH_RISK_KEYWORDS.items():
        if phrase in lower:
            score += weight
            detected.append(phrase)

    for phrase, weight in MEDIUM_RISK_KEYWORDS.items():
        if phrase in lower and phrase not in detected:
            score += weight
            detected.append(phrase)

    # Phone number pattern in suspicious context
    if re.search(r'07\d{8}', text) and any(k in lower for k in ["send", "pin", "claim"]):
        score += 15
        detected.append("suspicious phone number")

    # URL in message
    if re.search(r'https?://|bit\.ly|tinyurl', lower):
        score += 20
        detected.append("suspicious link")

    score = min(score, 100)
    return round(score, 2), detected


def _ml_score(text: str) -> Tuple[float, str]:
    """Return (confidence 0-100, method_used)."""
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.naive_bayes import MultinomialNB
        import numpy as np

        corpus = SCAM_SAMPLES + SAFE_SAMPLES
        labels = [1] * len(SCAM_SAMPLES) + [0] * len(SAFE_SAMPLES)

        vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=500)
        X = vectorizer.fit_transform(corpus)

        clf = MultinomialNB()
        clf.fit(X, labels)

        x_new = vectorizer.transform([text])
        proba = clf.predict_proba(x_new)[0]
        scam_prob = round(float(proba[1]) * 100, 2)
        return scam_prob, "ml"
    except ImportError:
        return -1.0, "keyword"


def analyze_message(text: str, sender: str = "") -> dict:
    """
    Main entry point. Returns a dict with:
      - is_scam (bool)
      - confidence_score (float 0-100)
      - detected_keywords (list)
      - method (str: 'ml' | 'keyword')
      - risk_level (str: 'High' | 'Medium' | 'Low' | 'Safe')
    """
    # Trusted sender override
    sender_lower = (sender or "").lower()
    if any(t in sender_lower for t in TRUSTED_SENDERS):
        return {
            "is_scam": False,
            "confidence_score": 0.0,
            "detected_keywords": [],
            "method": "trusted_sender",
            "risk_level": "Safe",
        }

    kw_score, detected = _keyword_score(text)
    ml_score, method = _ml_score(text)

    if method == "ml" and ml_score >= 0:
        # Blend: 60% ML + 40% keyword
        confidence = round(0.6 * ml_score + 0.4 * kw_score, 2)
    else:
        confidence = kw_score
        method = "keyword"

    is_scam = confidence >= 30

    if confidence >= 70:
        risk_level = "High"
    elif confidence >= 40:
        risk_level = "Medium"
    elif confidence >= 20:
        risk_level = "Low"
    else:
        risk_level = "Safe"

    return {
        "is_scam": is_scam,
        "confidence_score": confidence,
        "detected_keywords": detected,
        "method": method,
        "risk_level": risk_level,
    }
