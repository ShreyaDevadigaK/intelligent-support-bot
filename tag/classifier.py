# TAG: intent, sentiment, entity

import json
import openai
from tag.schemas import TagOutput

TAG_SYSTEM_PROMPT = """
You are a customer support message classifier.
Analyze the user message and return ONLY a valid JSON object.

JSON schema:
{
  "intent": one of [billing_dispute, cancel_request, refund_request,
                    technical_issue, general_inquiry, compliment, escalation_request],
  "sentiment": one of [positive, neutral, negative, very_negative],
  "entities": {extract amounts, dates, product names, invoice numbers},
  "needs_rag": true if the query requires looking up policies/docs, else false,
  "urgency": one of [low, medium, high, critical],
  "suggested_kb_topic": short phrase for what to search in the knowledge base
}

Rules:
- needs_rag = false for compliments, simple greetings, escalation_requests
- urgency = critical if user mentions legal action, public posting, or churn threat
- Return ONLY the JSON, no explanation, no markdown
"""

def classify_message(user_message: str) -> TagOutput:
    client = openai.OpenAI()
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",   # fast + cheap for classification
        messages=[
            {"role": "system", "content": TAG_SYSTEM_PROMPT},
            {"role": "user",   "content": user_message}
        ],
        temperature=0,         # deterministic classification
        max_tokens=300
    )
    
    raw = response.choices[0].message.content.strip()
    
    try:
        parsed = json.loads(raw)
        return TagOutput(**parsed)
    except Exception as e:
        # fallback: safe defaults if parsing fails
        return TagOutput(
            intent="general_inquiry",
            sentiment="neutral",
            entities={},
            needs_rag=True,
            urgency="low",
            suggested_kb_topic="general support"
        )