"""Graph node implementations.

Node responsibilities (mirrors the brief):
  extract_intent  -- LLM: read the conversation, pull out an order id / return intent
  lookup_order     -- deterministic: fetch the order from the mock DB
  check_eligibility -- deterministic: apply the 14-day Finnish return window
  approval_gate     -- deterministic + human-in-the-loop: auto-approve <=100EUR,
                        otherwise pause the graph (interrupt) for admin sign-off
  finalize           -- deterministic: send the (mocked) outcome email
  respond              -- LLM: turn the current state into a friendly reply
"""
from datetime import datetime
from typing import Literal

from langchain_core.messages import AIMessage, SystemMessage
from langgraph.types import interrupt
from pydantic import BaseModel, Field

from app_reference.agent.business import check_return_eligibility, find_order
from app_reference.agent.llm import get_llm
from app_reference.agent.state import AgentState
from app_reference.config import get_settings
from app_reference.database import SessionLocal
from app_reference.models import PendingApproval
from app_reference.services.email import send_email

settings = get_settings()


class IntentExtraction(BaseModel):
    order_id: str | None = Field(
        default=None, description="The order code mentioned by the customer, e.g. 'FI-10234'. Null if none given yet."
    )
    wants_return: bool = Field(
        default=False, description="True if the customer is asking to return an item / get a refund."
    )
    refund_amount: float | None = Field(
        default=None,
        description="A specific EUR amount the customer asked to be refunded, if they mentioned one. Otherwise null "
        "(the full order total will be used).",
    )


EXTRACTION_SYSTEM_PROMPT = """You are the intent-extraction step of a Finnish e-commerce support agent.
Read the conversation so far and extract structured fields about the customer's latest request.
Order codes look like "FI-10234". Only set wants_return=true if the customer clearly wants to return
an item or get a refund (not just asking about shipping status)."""


def extract_intent(state: AgentState) -> dict:
    llm = get_llm().with_structured_output(IntentExtraction)
    result: IntentExtraction = llm.invoke([SystemMessage(content=EXTRACTION_SYSTEM_PROMPT), *state["messages"]])

    update: dict = {"wants_return": result.wants_return}
    if result.order_id:
        update["order_id"] = result.order_id.strip().upper()
    if result.refund_amount is not None:
        update["refund_amount"] = result.refund_amount
    return update


def route_after_extract(state: AgentState) -> Literal["lookup_order", "respond"]:
    return "lookup_order" if state.get("order_id") else "respond"


def lookup_order(state: AgentState) -> dict:
    order = find_order(state["order_id"])
    return {"order": order}


def route_after_lookup(state: AgentState) -> Literal["check_eligibility", "respond"]:
    if not state.get("order") or not state.get("wants_return"):
        return "respond"
    return "check_eligibility"


def check_eligibility(state: AgentState) -> dict:
    eligibility = check_return_eligibility(state["order"])
    return {"eligibility": eligibility}


def route_after_eligibility(state: AgentState) -> Literal["approval_gate", "respond"]:
    return "approval_gate" if state["eligibility"]["eligible"] else "respond"


def approval_gate(state: AgentState) -> dict:
    """Deterministic amount check -- no side effects, safe to re-run.

    Split from escalation/interrupt on purpose: a LangGraph node re-executes
    from the top when it resumes after an interrupt(), so anything with a
    side effect (like writing the PendingApproval row) has to live in a node
    that completes *before* the interrupt, never in the interrupting node
    itself, or it would double-fire on resume.
    """
    order = state["order"]
    amount = state.get("refund_amount") or order["total_amount"]
    status = "auto_approved" if amount <= settings.auto_approve_refund_ceiling_eur else "pending"
    return {"refund_amount": amount, "approval_status": status}


def route_after_approval_gate(state: AgentState) -> Literal["escalate_for_approval", "finalize"]:
    return "escalate_for_approval" if state["approval_status"] == "pending" else "finalize"


def escalate_for_approval(state: AgentState) -> dict:
    """Runs exactly once (completes fully before the interrupt), so the
    PendingApproval row is written a single time even though the next node
    pauses/resumes."""
    order = state["order"]
    amount = state["refund_amount"]
    db = SessionLocal()
    try:
        row = PendingApproval(
            session_id=state["session_id"],
            order_id=order["id"],
            customer_email=order["customer_email"],
            refund_amount=amount,
            reason=f"Refund of {amount:.2f} EUR exceeds the {settings.auto_approve_refund_ceiling_eur:.0f} EUR "
            "auto-approve ceiling.",
            status="pending",
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return {"approval_id": row.id}
    finally:
        db.close()


def wait_for_decision(state: AgentState) -> dict:
    """The actual pause point. Nothing before `interrupt()` here has side
    effects, so re-running this node on resume is safe."""
    order = state["order"]
    decision = interrupt(
        {
            "type": "refund_approval_required",
            "approval_id": state["approval_id"],
            "order_id": order["id"],
            "customer_email": order["customer_email"],
            "refund_amount": state["refund_amount"],
            "message": f"Refund of {state['refund_amount']:.2f} EUR for order {order['id']} needs admin approval "
            f"(exceeds {settings.auto_approve_refund_ceiling_eur:.0f} EUR).",
        }
    )
    # Execution below only happens after a Command(resume=...) call.
    return {"approval_status": decision.get("decision", "rejected")}


def finalize(state: AgentState) -> dict:
    order = state["order"]
    status = state["approval_status"]
    amount = state["refund_amount"]

    if status in ("auto_approved", "approved"):
        subject = f"Your refund for order {order['id']} has been approved"
        body = (
            f"Hi {order['customer_name']},\n\n"
            f"Good news — your refund of {amount:.2f} EUR for order {order['id']} has been "
            f"{'automatically approved' if status == 'auto_approved' else 'approved by our support team'}. "
            "The amount will be credited back to your original payment method within 5-7 business days.\n\n"
            "Kind regards,\nCustomer Support"
        )
        note = f"Refund of {amount:.2f} EUR was {status.replace('_', ' ')}."
    else:
        subject = f"Update on your refund request for order {order['id']}"
        body = (
            f"Hi {order['customer_name']},\n\n"
            f"We've reviewed your refund request of {amount:.2f} EUR for order {order['id']}, and unfortunately "
            "it has not been approved at this time. Please reply to this email if you'd like more details.\n\n"
            "Kind regards,\nCustomer Support"
        )
        note = f"Refund of {amount:.2f} EUR was rejected."

    send_email(order["customer_email"], subject, body, order_id=order["id"])

    if state.get("approval_id"):
        db = SessionLocal()
        try:
            row = db.query(PendingApproval).filter(PendingApproval.id == state["approval_id"]).first()
            if row and row.status == "pending":
                row.status = status
                row.decided_at = datetime.utcnow()
                db.commit()
        finally:
            db.close()

    return {"outcome_note": note}


RESPOND_SYSTEM_PROMPT = """You are a friendly, concise Finnish e-commerce customer support agent.
Write ONE short reply (2-4 sentences) to the customer using the CONTEXT block below. Be warm and
specific (mention amounts/dates when relevant). Do not invent policy details beyond what's given."""


def respond(state: AgentState) -> dict:
    context_lines = [f"wants_return={state.get('wants_return')}"]
    if state.get("order_id") and not state.get("order"):
        context_lines.append(f"No order found for id '{state['order_id']}'. Ask the customer to double-check it.")
    if state.get("order"):
        context_lines.append(f"order={state['order']}")
    if state.get("eligibility"):
        context_lines.append(f"eligibility={state['eligibility']}")
    if state.get("approval_status") == "pending":
        context_lines.append(
            "This refund has just been escalated to a human admin for approval because it exceeds the "
            f"{settings.auto_approve_refund_ceiling_eur:.0f} EUR auto-approve ceiling. Tell the customer their "
            "request is submitted and under review, and they'll be emailed the decision."
        )
    elif state.get("outcome_note"):
        context_lines.append(f"outcome={state['outcome_note']}. A confirmation email has been sent.")
    if not state.get("order_id"):
        context_lines.append("No order id has been provided yet; ask the customer for their order code (e.g. FI-10234).")

    context = "\n".join(context_lines)
    llm = get_llm()
    ai_message: AIMessage = llm.invoke(
        [SystemMessage(content=RESPOND_SYSTEM_PROMPT + "\n\nCONTEXT:\n" + context), *state["messages"]]
    )
    return {"messages": [ai_message]}
