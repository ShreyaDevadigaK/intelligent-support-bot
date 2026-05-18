# Intelligent Customer Support Bot

A smart, AI-powered customer support chatbot that automatically handles customer inquiries with **intelligent routing**, **sentiment analysis**, and **knowledge-base retrieval**. Built for SaaS companies that want to provide fast, accurate, and personalized support responses.

---

## 🎯 What Does It Do?

This bot analyzes every incoming customer message and:

1. **Understands Intent** — Detects whether the customer is asking about billing, cancellations, technical issues, refunds, or something else
2. **Reads Sentiment** — Identifies if they're happy, neutral, frustrated, or very upset
3. **Prioritizes Urgency** — Flags critical cases (legal threats, public complaints) for immediate escalation
4. **Searches Your Docs** — Finds relevant answers from your knowledge base using AI-powered semantic search
5. **Generates Smart Responses** — Crafts personalized answers tailored to the customer's mood and need

**Result:** Faster resolutions, happier customers, fewer manual escalations.

---

## 🏗️ How It Works

The bot uses three core systems:

### **1. TAG System** (Intent & Sentiment Classifier)
- Uses OpenAI GPT-4o-mini to analyze customer messages
- Extracts intents: `billing_dispute`, `cancel_request`, `refund_request`, `technical_issue`, etc.
- Detects sentiment: `positive`, `neutral`, `negative`, `very_negative`
- Identifies urgency levels: `low`, `medium`, `high`, `critical`

### **2. RAG System** (Retrieval-Augmented Generation)
- Stores your support docs (FAQs, policies, pricing, etc.) in a Pinecone vector database
- When a customer asks a question, it searches for the most relevant doc chunks
- Passes those chunks to an LLM to generate an accurate, sourced answer
- Cites sources so customers know exactly where the answer came from

### **3. Router System** (Decision Gate)
- Routes messages based on TAG output:
  - **Compliments** → Direct acknowledgment (no search needed)
  - **Critical cases** → Immediate escalation to a human agent
  - **Everything else** → RAG lookup + personalized response

---

## ✨ Key Features

✅ **Fast Classification** — Analyzes intent, sentiment, and urgency in milliseconds  
✅ **No Hallucination** — Only answers based on your actual policies (won't make up info)  
✅ **Multi-Language Ready** — Works with messages in any language  
✅ **Sentiment-Aware** — Adjusts tone based on customer mood  
✅ **Escalation Smart** — Catches critical cases and routes them to humans immediately  
✅ **Source Attribution** — Every answer cites where it came from  

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- API keys for:
  - **OpenAI** (GPT-4o for classification and generation)
  - **Pinecone** (Vector database for your knowledge base)

### 1. Clone & Install

```bash
git clone https://github.com/<your-username>/intelligent-support-bot.git
cd intelligent-support-bot
pip install -r requirements.txt
```

### 2. Set Up Environment

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=sk-proj-...
PINECONE_API_KEY=pcsk_...
PINECONE_INDEX=support-kb
```

### 3. Index Your Docs

Place your support documents in `data/docs/` as `.txt` files (e.g., `billing-faq.txt`, `refund-policy.txt`).

Then index them:

```bash
python rag/indexer.py
```

This splits your docs into chunks, embeds them, and stores them in Pinecone.

### 4. Run the Server

```bash
uvicorn main:app --reload
```

Visit `http://localhost:8000` and start chatting!

---

## 📝 Example Conversation

**Customer:** *"I was charged twice last month!"*

**Bot Analysis:**
- Intent: `billing_dispute`
- Sentiment: `very_negative` (frustrated)
- Urgency: `high`
- Needs RAG: `True`

**Bot searches your docs** for billing and refund policies, then responds:

> "I sincerely apologize for the double charge. This shouldn't have happened. According to our Refund Policy, duplicate charges are refunded within 2 business days. I've flagged your case for priority review. You should see the refund by [date]. I'm escalating this to our billing team for immediate attention — someone will contact you within 1 hour."
---

## 📁 Project Structure

```
├── main.py                 # FastAPI app & endpoints
├── tag/
│   ├── classifier.py       # Intent & sentiment classifier
│   └── schemas.py          # Data models
├── rag/
│   ├── indexer.py          # Indexes docs into Pinecone
│   ├── retriever.py        # Searches vector DB
│   └── generator.py        # Generates responses with LLM
├── router/
│   └── decision_gate.py     # Routes based on TAG output
├── data/docs/              # Your support docs (FAQs, policies, etc.)
├── tests/
│   └── test_pipeline.py    # Unit tests
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

---

## 🧪 Run Tests

```bash
pytest tests/
```

Note: Tests require `OPENAI_API_KEY` set in `.env`.

---
**Happy supporting! 🚀**
