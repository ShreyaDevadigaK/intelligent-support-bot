# FastAPI entry point

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from tag.classifier import classify_message
from rag.retriever import retrieve
from rag.generator import generate_response
from router.decision_gate import route

load_dotenv()
app = FastAPI(title="Support Bot - RAG + TAG")


class MessageRequest(BaseModel):
    message: str
    user_id: str = "anonymous"


class BotResponse(BaseModel):
    answer: str
    intent: str
    sentiment: str
    urgency: str
    sources: list[str]
    used_rag: bool


@app.get("/", response_class=HTMLResponse)
def home():
    return """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Support Bot</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f5f7fb;
      --panel: #ffffff;
      --ink: #172033;
      --muted: #667085;
      --line: #d9e0ea;
      --accent: #0f766e;
      --accent-dark: #115e59;
      --soft: #e8f5f3;
      --danger: #b42318;
      --shadow: 0 18px 45px rgba(28, 39, 63, 0.12);
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      min-height: 100vh;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--ink);
      background:
        linear-gradient(180deg, rgba(15, 118, 110, 0.08), transparent 34%),
        var(--bg);
    }

    main {
      width: min(1060px, calc(100% - 32px));
      margin: 0 auto;
      padding: 32px 0;
    }

    .topbar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
      margin-bottom: 18px;
    }

    h1 {
      margin: 0;
      font-size: clamp(26px, 3vw, 42px);
      font-weight: 760;
      letter-spacing: 0;
    }

    .health {
      border: 1px solid var(--line);
      background: var(--panel);
      border-radius: 999px;
      padding: 8px 12px;
      color: var(--muted);
      font-size: 14px;
      white-space: nowrap;
    }

    .layout {
      display: grid;
      grid-template-columns: minmax(0, 1.45fr) minmax(280px, 0.75fr);
      gap: 18px;
      align-items: start;
    }

    .chat, .details {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      box-shadow: var(--shadow);
    }

    .chat {
      min-height: 620px;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }

    .messages {
      flex: 1;
      padding: 22px;
      overflow-y: auto;
    }

    .message {
      width: fit-content;
      max-width: min(680px, 92%);
      padding: 14px 16px;
      border-radius: 8px;
      line-height: 1.5;
      font-size: 15px;
      white-space: pre-wrap;
      overflow-wrap: anywhere;
      margin-bottom: 14px;
    }

    .message.user {
      margin-left: auto;
      background: var(--accent);
      color: white;
    }

    .message.bot {
      background: #f2f5f9;
      color: var(--ink);
      border: 1px solid #e3e8ef;
    }

    .composer {
      border-top: 1px solid var(--line);
      padding: 16px;
      background: #fbfcfe;
    }

    textarea {
      width: 100%;
      min-height: 104px;
      resize: vertical;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px;
      font: inherit;
      line-height: 1.5;
      color: var(--ink);
      outline: none;
      background: white;
    }

    textarea:focus {
      border-color: var(--accent);
      box-shadow: 0 0 0 3px rgba(15, 118, 110, 0.14);
    }

    .actions {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      margin-top: 12px;
    }

    button {
      border: 0;
      border-radius: 8px;
      background: var(--accent);
      color: white;
      font: inherit;
      font-weight: 700;
      padding: 11px 18px;
      cursor: pointer;
      min-width: 112px;
    }

    button:hover { background: var(--accent-dark); }
    button:disabled { opacity: 0.6; cursor: wait; }

    .hint {
      color: var(--muted);
      font-size: 13px;
      line-height: 1.4;
    }

    .details {
      padding: 18px;
    }

    .details h2 {
      font-size: 16px;
      margin: 0 0 14px;
    }

    .chip-grid {
      display: grid;
      gap: 10px;
      margin-bottom: 18px;
    }

    .chip {
      display: flex;
      justify-content: space-between;
      gap: 10px;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 10px 12px;
      background: #fbfcfe;
      font-size: 14px;
    }

    .chip span:first-child { color: var(--muted); }
    .chip span:last-child { font-weight: 700; text-align: right; }

    .sources {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      min-height: 32px;
    }

    .source {
      border-radius: 999px;
      background: var(--soft);
      color: var(--accent-dark);
      padding: 7px 10px;
      font-size: 13px;
      font-weight: 700;
    }

    .error {
      color: var(--danger);
      font-size: 14px;
      margin-top: 12px;
      min-height: 20px;
    }

    @media (max-width: 780px) {
      main { width: min(100% - 20px, 1060px); padding-top: 18px; }
      .topbar { align-items: flex-start; flex-direction: column; }
      .layout { grid-template-columns: 1fr; }
      .chat { min-height: 540px; }
      .actions { align-items: stretch; flex-direction: column; }
      button { width: 100%; }
    }
  </style>
</head>
<body>
  <main>
    <div class="topbar">
      <h1>Customer Support Bot</h1>
      <div class="health">FastAPI UI for /chat</div>
    </div>

    <section class="layout">
      <div class="chat">
        <div class="messages" id="messages">
          <div class="message bot">Hi. Type a customer support message below and I will classify it, retrieve relevant policy docs, and answer from the knowledge base.</div>
        </div>

        <form class="composer" id="chatForm">
          <textarea id="messageInput" placeholder="Example: I was charged twice this month. Can I get a refund?"></textarea>
          <div class="actions">
            <div class="hint">This sends a POST request to <strong>/chat</strong> with your message.</div>
            <button id="sendButton" type="submit">Send</button>
          </div>
          <div class="error" id="errorBox"></div>
        </form>
      </div>

      <aside class="details">
        <h2>Last Analysis</h2>
        <div class="chip-grid">
          <div class="chip"><span>Intent</span><span id="intent">-</span></div>
          <div class="chip"><span>Sentiment</span><span id="sentiment">-</span></div>
          <div class="chip"><span>Urgency</span><span id="urgency">-</span></div>
          <div class="chip"><span>Used RAG</span><span id="usedRag">-</span></div>
        </div>

        <h2>Sources</h2>
        <div class="sources" id="sources">
          <span class="source">No sources yet</span>
        </div>
      </aside>
    </section>
  </main>

  <script>
    const form = document.getElementById("chatForm");
    const input = document.getElementById("messageInput");
    const messages = document.getElementById("messages");
    const button = document.getElementById("sendButton");
    const errorBox = document.getElementById("errorBox");

    function addMessage(text, role) {
      const bubble = document.createElement("div");
      bubble.className = `message ${role}`;
      bubble.textContent = text;
      messages.appendChild(bubble);
      messages.scrollTop = messages.scrollHeight;
      return bubble;
    }

    function setText(id, value) {
      document.getElementById(id).textContent = value || "-";
    }

    function updateSources(sources) {
      const box = document.getElementById("sources");
      box.innerHTML = "";
      if (!sources || sources.length === 0) {
        const empty = document.createElement("span");
        empty.className = "source";
        empty.textContent = "No sources";
        box.appendChild(empty);
        return;
      }
      sources.forEach((source) => {
        const item = document.createElement("span");
        item.className = "source";
        item.textContent = source;
        box.appendChild(item);
      });
    }

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const text = input.value.trim();
      if (!text) {
        errorBox.textContent = "Enter a message first.";
        return;
      }

      errorBox.textContent = "";
      button.disabled = true;
      button.textContent = "Sending...";
      addMessage(text, "user");
      const loading = addMessage("Thinking...", "bot");
      input.value = "";

      try {
        const response = await fetch("/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: text })
        });

        if (!response.ok) {
          throw new Error(`Request failed with status ${response.status}`);
        }

        const data = await response.json();
        loading.textContent = data.answer;
        setText("intent", data.intent);
        setText("sentiment", data.sentiment);
        setText("urgency", data.urgency);
        setText("usedRag", data.used_rag ? "Yes" : "No");
        updateSources(data.sources);
      } catch (error) {
        loading.textContent = "Something went wrong while calling the API.";
        errorBox.textContent = error.message;
      } finally {
        button.disabled = false;
        button.textContent = "Send";
        input.focus();
      }
    });
  </script>
</body>
</html>
"""


@app.post("/chat", response_model=BotResponse)
async def chat(req: MessageRequest):
    # STEP 1: TAG
    tag = classify_message(req.message)

    # STEP 2: ROUTE
    decision = route(tag)

    # STEP 3a: Skip RAG if not needed
    if decision.skip_rag:
        return BotResponse(
            answer=decision.response_override,
            intent=tag.intent,
            sentiment=tag.sentiment,
            urgency=tag.urgency,
            sources=[],
            used_rag=False,
        )

    # STEP 3b: RAG
    query = tag.suggested_kb_topic or req.message
    chunks = retrieve(query, top_k=4)

    if not chunks:
        # No relevant docs found: honest fallback
        return BotResponse(
            answer="I couldn't find a specific policy for this. Let me connect you with a support agent who can help directly.",
            intent=tag.intent,
            sentiment=tag.sentiment,
            urgency=tag.urgency,
            sources=[],
            used_rag=True,
        )

    # STEP 4: GENERATE
    result = generate_response(req.message, chunks, tag)

    return BotResponse(
        answer=result["answer"],
        intent=tag.intent,
        sentiment=tag.sentiment,
        urgency=tag.urgency,
        sources=result["sources"],
        used_rag=True,
    )


@app.get("/health")
def health():
    return {"status": "ok"}
