const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const detail = await res.json().catch(() => ({}));
    throw new Error(detail.detail || `Request failed: ${res.status}`);
  }
  return res.status === 204 ? null : res.json();
}

export const api = {
  sendMessage: (sessionId, message) =>
    request("/chat", {
      method: "POST",
      body: JSON.stringify({ session_id: sessionId, message }),
    }),

  getMessages: (sessionId) => request(`/chat/${sessionId}/messages`),

  listOrders: () => request("/orders"),
  getOrder: (orderId) => request(`/orders/${orderId}`),

  listPendingApprovals: (status) =>
    request(`/admin/pending-approvals${status ? `?status=${status}` : ""}`),

  decideApproval: (approvalId, decision, note = "", decidedBy = "admin") =>
    request(`/admin/approvals/${approvalId}/decision`, {
      method: "POST",
      body: JSON.stringify({ decision, note, decided_by: decidedBy }),
    }),

  listSentEmails: () => request("/admin/emails"),
};
