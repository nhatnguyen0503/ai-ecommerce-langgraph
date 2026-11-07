import type { ApprovalDecision } from "../types/api";
import {
  useDecideApprovalMutation,
  useListPendingApprovalsQuery,
  useListSentEmailsQuery,
} from "../services/agentApi";
import { queryErrorText } from "../services/queryError";
import OrdersTable from "./OrdersTable";

const POLL_MS = 5000;

function formatDate(iso: string | null): string {
  if (!iso) return "";
  return new Date(iso).toLocaleString();
}

export default function AdminDashboard() {
  const { data: approvals = [], error: approvalsError } =
    useListPendingApprovalsQuery(undefined, { pollingInterval: POLL_MS });
  const { data: emails = [], error: emailsError } = useListSentEmailsQuery(
    undefined,
    {
      pollingInterval: POLL_MS,
    },
  );
  const [
    decideApproval,
    { isLoading: deciding, originalArgs, error: decideError },
  ] = useDecideApprovalMutation();

  const busyId = deciding ? originalArgs?.approvalId : null;
  const error = queryErrorText(
    approvalsError ?? emailsError ?? decideError,
    "Failed to load admin data.",
  );

  async function handleDecision(id: string, decision: ApprovalDecision) {
    try {
      await decideApproval({ approvalId: id, decision }).unwrap();
    } catch {
      /* error is already exposed as decideError */
    }
  }

  const pending = approvals.filter((a) => a.status === "pending");
  const decided = approvals.filter((a) => a.status !== "pending").slice(0, 10);

  return (
    <div>
      {error && (
        <div
          className="status-banner"
          style={{ background: "#fbe3e3", color: "#c23636" }}
        >
          {error}
        </div>
      )}
      <OrdersTable />

      <div className="card">
        <h2 className="section-title" style={{ marginTop: 0 }}>
          Refunds awaiting approval ({pending.length})
        </h2>
        {pending.length === 0 && (
          <div className="empty-state">Nothing waiting on you right now.</div>
        )}
        <div className="approval-list">
          {pending.map((a) => (
            <div
              key={a.id}
              className="approval-item card"
              style={{ padding: 12 }}
            >
              <div>
                <div>
                  <span className="amount">
                    EUR {a.refund_amount.toFixed(2)}
                  </span>{" "}
                  <span className="badge pending">pending</span>
                </div>
                <div className="approval-meta">
                  Order {a.order_id} -- {a.customer_email}
                </div>
                <div className="approval-meta">{a.reason}</div>
                <div className="approval-meta">
                  Requested {formatDate(a.created_at)}
                </div>
              </div>
              <div className="decision-buttons">
                <button
                  className="approve-btn"
                  disabled={busyId === a.id}
                  onClick={() => handleDecision(a.id, "approved")}
                >
                  Approve
                </button>
                <button
                  className="reject-btn"
                  disabled={busyId === a.id}
                  onClick={() => handleDecision(a.id, "rejected")}
                >
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
              <div
                key={a.id}
                className="approval-item card"
                style={{ padding: 12 }}
              >
                <div>
                  <div>
                    <span className="amount">
                      EUR {a.refund_amount.toFixed(2)}
                    </span>{" "}
                    <span className={`badge ${a.status}`}>{a.status}</span>
                  </div>
                  <div className="approval-meta">
                    Order {a.order_id} -- {a.customer_email}
                  </div>
                  <div className="approval-meta">
                    Decided {formatDate(a.decided_at)} by {a.decided_by}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </>
      )}

      <h2 className="section-title">Outbound email log (mocked)</h2>
      <div className="card email-list">
        {emails.length === 0 && (
          <div className="empty-state">No emails sent yet.</div>
        )}
        {emails.slice(0, 15).map((e) => (
          <div key={e.id} className="email-item">
            <div className="subject">
              {e.subject}{" "}
              <span className="approval-meta">-&gt; {e.to_email}</span>
            </div>
            <div className="body">{e.body}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
