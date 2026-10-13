import React, { useCallback, useEffect, useState } from "react";
import { api } from "../api.js";

function formatDate(iso) {
  if (!iso) return "";
  return new Date(iso).toLocaleString();
}

export default function AdminDashboard() {
  const [approvals, setApprovals] = useState([]);
  const [emails, setEmails] = useState([]);
  const [busyId, setBusyId] = useState(null);
  const [error, setError] = useState("");

  const refresh = useCallback(async () => {
    try {
      const [allApprovals, allEmails] = await Promise.all([api.listPendingApprovals(), api.listSentEmails()]);
      setApprovals(allApprovals);
      setEmails(allEmails);
    } catch (err) {
      setError(err.message || "Failed to load admin data.");
    }
  }, []);

  useEffect(() => {
    refresh();
    const id = setInterval(refresh, 5000);
    return () => clearInterval(id);
  }, [refresh]);

  async function handleDecision(id, decision) {
    setBusyId(id);
    setError("");
    try {
      await api.decideApproval(id, decision);
      await refresh();
    } catch (err) {
      setError(err.message || "Failed to record decision.");
    } finally {
      setBusyId(null);
    }
  }

  const pending = approvals.filter((a) => a.status === "pending");
  const decided = approvals.filter((a) => a.status !== "pending").slice(0, 10);

  return (
    <div>
      {error && (
        <div className="status-banner" style={{ background: "#fbe3e3", color: "#c23636" }}>
          {error}
        </div>
      )}

      <div className="card">
        <h2 className="section-title" style={{ marginTop: 0 }}>
          Refunds awaiting approval ({pending.length})
        </h2>
        {pending.length === 0 && <div className="empty-state">Nothing waiting on you right now.</div>}
        <div className="approval-list">
          {pending.map((a) => (
            <div key={a.id} className="approval-item card" style={{ padding: 12 }}>
              <div>
                <div>
                  <span className="amount">EUR {a.refund_amount.toFixed(2)}</span>{" "}
                  <span className="badge pending">pending</span>
                </div>
                <div className="approval-meta">
                  Order {a.order_id} -- {a.customer_email}
                </div>
                <div className="approval-meta">{a.reason}</div>
                <div className="approval-meta">Requested {formatDate(a.created_at)}</div>
              </div>
              <div className="decision-buttons">
                <button className="approve-btn" disabled={busyId === a.id} onClick={() => handleDecision(a.id, "approved")}>
                  Approve
                </button>
                <button className="reject-btn" disabled={busyId === a.id} onClick={() => handleDecision(a.id, "rejected")}>
                  Reject
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {decided.length > 0 && (
        <>
          <h2 className="section-title">Recently decided</h2>
          <div className="approval-list">
            {decided.map((a) => (
              <div key={a.id} className="approval-item card" style={{ padding: 12 }}>
                <div>
                  <div>
                    <span className="amount">EUR {a.refund_amount.toFixed(2)}</span>{" "}
                    <span className={`badge ${a.status}`}>{a.status}</span>
                  </div>
                  <div className="approval-meta">
                    Order {a.order_id} -- {a.customer_email}
                  </div>
                  <div className="approval-meta">Decided {formatDate(a.decided_at)} by {a.decided_by}</div>
                </div>
              </div>
            ))}
          </div>
        </>
      )}

      <h2 className="section-title">Outbound email log (mocked)</h2>
      <div className="card email-list">
        {emails.length === 0 && <div className="empty-state">No emails sent yet.</div>}
        {emails.slice(0, 15).map((e) => (
          <div key={e.id} className="email-item">
            <div className="subject">
              {e.subject} <span className="approval-meta">-&gt; {e.to_email}</span>
            </div>
            <div className="body">{e.body}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
