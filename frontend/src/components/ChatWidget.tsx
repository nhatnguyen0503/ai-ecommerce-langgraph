import { useEffect, useRef, useState, type FormEvent } from "react";
import type { FetchBaseQueryError } from "@reduxjs/toolkit/query";
import {
  useGetMessagesQuery,
  useSendMessageMutation,
} from "../services/agentApi";
import { queryErrorText } from "../services/queryError";
import { useAppDispatch, useAppSelector } from "../hooks";
import {
  awaitingApprovalChanged,
  messagesLoaded,
  sendFailed,
  sendFinished,
  sendStarted,
  userMessageAdded,
} from "../features/chat/chatSlice";

export default function ChatWidget() {
  const dispatch = useAppDispatch();
  const { sessionId, messages, sending, awaitingApproval, error } =
    useAppSelector((state) => state.chat);
  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // One query does both jobs: initial load, and polling while a refund awaits approval.
  const { data: serverMessages } = useGetMessagesQuery(sessionId, {
    pollingInterval: awaitingApproval ? 5000 : 0, // 0 = no polling
  });
  const [sendMessage] = useSendMessageMutation();

  // Sync server history into the slice when the server has more than we show.
  useEffect(() => {
    if (!serverMessages) return;
    if (serverMessages.length > messages.length) {
      dispatch(messagesLoaded(serverMessages));
      dispatch(awaitingApprovalChanged(false));
    }
  }, [serverMessages, messages.length, dispatch]);

  async function handleSend(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const text = input.trim();
    if (!text || sending) return;

    dispatch(userMessageAdded(text));
    setInput("");
    dispatch(sendStarted());

    try {
      const res = await sendMessage({ sessionId, message: text }).unwrap();
      // The backend returns the authoritative history for the messages that
      // made it into a checkpoint. When the graph paused for approval, its
      // own "respond" node never ran, so `res.reply` is a synthetic
      // "submitted for review" notice that only exists client-side here.
      const base =
        res.messages && res.messages.length ? res.messages : messages;
      dispatch(
        messagesLoaded(
          res.status === "awaiting_approval"
            ? [...base, { role: "assistant", content: res.reply }]
            : base,
        ),
      );
      dispatch(awaitingApprovalChanged(res.status === "awaiting_approval"));
    } catch (err) {
      dispatch(
        sendFailed(
          queryErrorText(
            err as FetchBaseQueryError,
            "Something went wrong talking to the support agent.",
          ),
        ),
      );
    } finally {
      dispatch(sendFinished());
    }
  }

  return (
    <div className="card chat-card">
      {awaitingApproval && (
        <div className="status-banner">
          A refund on this conversation is waiting for admin approval. This chat
          will update automatically once it's decided.
        </div>
      )}
      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="empty-state">
            Try: "What's the status of order FI-10236?" or "I want to return
            order FI-10236, it doesn't fit."
          </div>
        )}
        {messages.map((m, i) => (
          <div
            key={i}
            className={`bubble ${m.role === "user" ? "user" : "assistant"}`}
          >
            {m.content}
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
      {error && (
        <div
          className="status-banner"
          style={{ background: "#fbe3e3", color: "#c23636" }}
        >
          {error}
        </div>
      )}
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
      <div className="hint">
        Session: {sessionId} -- sample order codes: FI-10234, FI-10235,
        FI-10236, FI-10237, FI-10238
      </div>
    </div>
  );
}
