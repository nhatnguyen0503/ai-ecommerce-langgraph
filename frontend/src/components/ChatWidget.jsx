import React, { useEffect, useRef, useState } from "react";
import { api } from "../api.js";

function makeSessionId() {
  return `sess_${Math.random().toString(36).slice(2, 10)}${Date.now().toString(36)}`;
}

function getOrCreateSessionId() {
  try {
    const existing = window.localStorage.getItem("support_session_id");
    if (existing) return existing;
    const fresh = makeSessionId();
    window.localStorage.setItem("support_session_id", fresh);
    return fresh;
  } catch {
    // localStorage unavailable (private mode etc.) -- fall back to an in-memory id
    return makeSessionId();
  }
}

export default function ChatWidget() {
  const [sessionId] = useState(getOrCreateSessionId);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [awaitingApproval, setAwaitingApproval] = useState(false);
  const [error, setError] = useState("");
  const bottomRef = useRef(null);
  const pollRef = useRef(null);

  useEffect(() => {
    api
      .getMessages(sessionId)
      .then((msgs) => setMessages(msgs))
      .catch(() => {});
  }, [sessionId]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // While a refund is escalated to an admin, poll for the follow-up message
  // that appears once the graph resumes after a decision.
  useEffect(() => {
    if (!awaitingApproval) {
      clearInterval(pollRef.current);
      return;
    }
    pollRef.current = setInterval(async () => {
      try {
        const msgs = await api.getMessages(sessionId);
        if (msgs.length > messages.length) {
          setMessages(msgs);
          setAwaitingApproval(false);
        }
      } catch {
        /* ignore transient errors while polling */
      }
    }, 4000);
    return () => clearInterval(pollRef.current);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [awaitingApproval, messages.length, sessionId]);

  async function handleSend(e) {
    e.preventDefault();
    const text = input.trim();
    if (!text || sending) return;

    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setInput("");
    setSending(true);
    setError("");

    try {
      const res = await api.sendMessage(sessionId, text);
      // The backend returns the authoritative history for the messages that
      // made it into a checkpoint. When the graph paused for approval, its
      // own "respond" node never ran, so `res.reply` is a synthetic
      // "submitted for review" notice that only exists client-side here.
      const base = res.messages && res.messages.length ? res.messages : messages;
      setMessages(
        res.status === "awaiting_approval" ? [...base, { role: "assistant", content: res.reply }] : base
      );
      setAwaitingApproval(res.status === "awaiting_approval");
    } catch (err) {
      setError(err.message || "Something went wrong talking to the support agent.");
    } finally {
      setSending(false);
    }
  }

  return (
    <div className="card chat-card">
      {awaitingApproval && (
        <div className="status-banner">
          A refund on this conversation is waiting for admin approval. This chat will update automatically once
          it's decided.
        </div>
      )}
      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="empty-state">
            Try: "What's the status of order FI-10236?" or "I want to return order FI-10236, it doesn't fit."
          </div>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`bubble ${m.role === "user" ? "user" : "assistant"}`}>
            {m.content}
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
      {error && <div className="status-banner" style={{ background: "#fbe3e3", color: "#c23636" }}>{error}</div>}
      <form className="chat-input-row" onSubmit={handleSend}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about an order or request a return..."
          disabled={sending}
        />
        <button type="submit" disabled={sending || !input.trim()}>
          {sending ? "Sending..." : "Send"}
        </button>
      </form>
      <div className="hint">Session: {sessionId} -- sample order codes: FI-10234, FI-10235, FI-10236, FI-10237, FI-10238</div>
    </div>
  );
}
