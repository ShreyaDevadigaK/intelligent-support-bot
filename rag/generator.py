# LLM response generation

import openai
from tag.schemas import TagOutput

def build_system_prompt(tag: TagOutput) -> str:
    tone = {
        "positive":      "Be warm and appreciative.",
        "neutral":       "Be clear, professional, and helpful.",
        "negative":      "Be empathetic and solution-focused. Acknowledge their frustration.",
        "very_negative": "Lead with a sincere apology. Be calm, empathetic, and decisive."
    }[tag.sentiment]
    
    urgency_note = ""
    if tag.urgency == "critical":
        urgency_note = "\nIMPORTANT: This is a critical case. Offer immediate escalation to a senior agent."
    
    return f"""You are a helpful customer support agent for AcmeSaaS.

Tone: {tone}{urgency_note}

Rules:
1. Answer ONLY based on the provided context documents
2. If the answer isn't in the context, say so honestly — never invent policies
3. Always cite your source (e.g., "Per our Refund Policy...")
4. If intent is 'cancel_request', acknowledge and offer a retention alternative first
5. Keep responses under 150 words unless complexity requires more
6. End with a clear next step or offer further help
"""

def generate_response(
    user_message: str,
    retrieved_chunks: list[dict],
    tag: TagOutput
) -> dict:
    
    # Build context block from retrieved docs
    context = "\n\n---\n\n".join([
        f"[Source: {c['source']}]\n{c['text']}"
        for c in retrieved_chunks
    ])
    
    user_prompt = f"""Context documents:
{context}

---

Customer message: {user_message}

Entities detected: {tag.entities}
Customer intent:   {tag.intent}
"""
    
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": build_system_prompt(tag)},
            {"role": "user",   "content": user_prompt}
        ],
        temperature=0.3,
        max_tokens=400
    )
    
    return {
        "answer":  response.choices[0].message.content,
        "sources": list({c["source"] for c in retrieved_chunks})
    }