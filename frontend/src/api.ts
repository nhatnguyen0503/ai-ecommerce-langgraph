import type {
  ApiErrorBody,
  ApprovalDecision,
  ChatMessage,
  ChatResponse,
  DecisionResult,
  Order,
  PendingApproval,
  ReturnEligibility,
  SentEmail,
} from "./types/api";

const BASE_URL: string = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly requestId: string | null,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

function errorMessage(body: ApiErrorBody | null, status: number): string {
  if (!body) return `Request failed: ${status}`;
  if (typeof body.detail === "string") return body.detail;
  // 422: detail is a list of validation errors
  return body.detail.map((e) => e.msg).join("; ");
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...options.headers },
  });

  if (!res.ok) {
    const body = (await res.json().catch(() => null)) as ApiErrorBody | null;
    throw new ApiError(res.status, body?.request_id ?? null, errorMessage(body, res.status));
  }

  return (res.status === 204 ? null : await res.json()) as T;
}

const enc = encodeURIComponent;

export const api = {
  // --- Orders (backend/app) ---
  listOrders: () => request<Order[]>("/orders"),
  getOrder: (orderId: string) => request<Order>(`/orders/${enc(orderId)}`),
  getReturnEligibility: (orderId: string) =>
    request<ReturnEligibility>(`/orders/${enc(orderId)}/return-eligibility`),

  // --- Chat (TODO: only in backend/app_reference for now) ---
  sendMessage: (sessionId: string, message: string) =>
    request<ChatResponse>("/chat", {
      method: "POST",
      body: JSON.stringify({ session_id: sessionId, message }),
    }),
  getMessages: (sessionId: string) =>
    request<ChatMessage[]>(`/chat/${enc(sessionId)}/messages`),

  // --- Admin (TODO: only in backend/app_reference for now) ---
  listPendingApprovals: (status?: string) =>
    request<PendingApproval[]>(
      `/admin/pending-approvals${status ? `?status=${enc(status)}` : ""}`,
    ),
  decideApproval: (
    approvalId: string,
    decision: ApprovalDecision,
    note = "",
    decidedBy = "admin",
  ) =>
    request<DecisionResult>(`/admin/approvals/${enc(approvalId)}/decision`, {
      method: "POST",
      body: JSON.stringify({ decision, note, decided_by: decidedBy }),
    }),
  listSentEmails: () => request<SentEmail[]>("/admin/emails"),
};

/** Turn any thrown value into a user-facing message, with request id when available. */
export function errorText(err: unknown, fallback: string): string {
  const msg = err instanceof Error && err.message ? err.message : fallback;
  return err instanceof ApiError && err.requestId ? `${msg} (request id: ${err.requestId})` : msg;
}