# Pydantic models for TAG output

from pydantic import BaseModel
from typing import Literal, Optional

class TagOutput(BaseModel):
    intent: Literal[
        "billing_dispute",
        "cancel_request", 
        "refund_request",
        "technical_issue",
        "general_inquiry",
        "compliment",
        "escalation_request"
    ]
    sentiment: Literal["positive", "neutral", "negative", "very_negative"]
    entities: dict  # e.g. {"amount": "$49", "date": "last month"}
    needs_rag: bool          # TAG decides if RAG is even needed
    urgency: Literal["low", "medium", "high", "critical"]
    suggested_kb_topic: Optional[str]  # hint for RAG retrieval