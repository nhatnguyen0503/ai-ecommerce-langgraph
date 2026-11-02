// Mirrors backend/app/schemas.py - keep in sync when the Pydantic models change.

export interface OrderItem {
    name: string;
    qty: number;
    price: number;
}

export interface Order {
    id: string;
    customer_name: string;
    customer_email: string;
    items: OrderItem[];
    total_amount: number;
    currency: string;
    status: string;
    warehouse: string;
    order_date: string; // ISO 8601 datetime string (JSON has no Date type)
    delivered_date: string | null;
}

export interface ReturnEligibility {
    eligible: boolean;
    days_since_delivery: number | null;
    reason: string;
}

// Mirrors error_response()  in backend/app/errors.py
// For 422 validation errors FastAPI returns `detail` as a list of objects
export interface ApiErrorBody {
    detail: string | ValidationErrorItem[];
    request_id: string;
}

export interface ValidationErrorItem {
    loc: (string | number)[];
    msg: string;
    type: string;
}

// --- Chat & admin types ---
// Mirrors backend/app_reference/schemas.py. These endpoints are NOT in backend/app yet.
export type ChatRole = "user" | "assistant" | "system";

export interface ChatMessage {
    role: ChatRole;
    content: string;
}

export interface ChatResponse {
    session_id: string;
    reply: string;
    status: "ok" | "awaiting_approval"
    messages: ChatMessage[];
}

export type ApprovalDecision = "approved" | "rejected";

export interface PendingApproval {
    id: string;
    session_id: string;
    order_id: string;
    customer_email: string;
    refund_amount: number;
    reason: string;
    status: string;
    created_at: string;
    decided_at: string | null;
    decided_by: string | null;
    admin_note: string | null;
}

export interface DecisionResult {
    approval_id: string;
    decision: ApprovalDecision;
    session_id: string;
    final_customer_message: string | null;
}

export interface SentEmail {
    id: string;
    to_email: string;
    subject: string;
    body: string;
    order_id: string | null;
    created_at: string;
}
