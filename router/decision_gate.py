# Routes based on TAG output

from tag.schemas import TagOutput
from dataclasses import dataclass
from typing import Literal

@dataclass
class RoutingDecision:
    action: Literal["rag", "direct_escalate", "direct_ack", "flag_critical"]
    skip_rag: bool
    response_override: str | None = None  # used when we skip RAG entirely

def route(tag: TagOutput) -> RoutingDecision:
    
    # Critical: threats of legal action, public shaming, etc.
    if tag.urgency == "critical":
        return RoutingDecision(
            action="flag_critical",
            skip_rag=True,
            response_override=(
                "I'm truly sorry about your experience. "
                "I'm escalating this to our senior support team right now — "
                "someone will contact you within 1 hour. "
                "Your case ID is being prioritized."
            )
        )
    
    # Compliments don't need doc lookup
    if tag.intent == "compliment":
        return RoutingDecision(
            action="direct_ack",
            skip_rag=True,
            response_override=(
                "Thank you so much — feedback like yours genuinely makes our day! "
                "We'll pass this along to the team. Is there anything else we can help with?"
            )
        )
    
    # Explicit escalation request
    if tag.intent == "escalation_request":
        return RoutingDecision(
            action="direct_escalate",
            skip_rag=True,
            response_override=(
                "Absolutely — I'm connecting you to a senior agent now. "
                "Average wait time is under 5 minutes. "
                "Your conversation history will transfer automatically."
            )
        )
    
    # Everything else: use RAG
    return RoutingDecision(action="rag", skip_rag=False)