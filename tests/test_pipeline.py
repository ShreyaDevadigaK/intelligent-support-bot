import pytest
from tag.classifier import classify_message

def test_billing_dispute_detected():
    tag = classify_message("I was charged twice last month, this is unacceptable!")
    assert tag.intent == "billing_dispute"
    assert tag.sentiment in ["negative", "very_negative"]
    assert tag.needs_rag == True

def test_compliment_skips_rag():
    tag = classify_message("Your support team is amazing, thank you!")
    assert tag.intent == "compliment"
    assert tag.needs_rag == False

def test_critical_urgency():
    tag = classify_message("I'll be posting about this on Twitter and contacting my lawyer.")
    assert tag.urgency == "critical"

def test_cancel_intent():
    tag = classify_message("I want to cancel my subscription immediately.")
    assert tag.intent == "cancel_request"