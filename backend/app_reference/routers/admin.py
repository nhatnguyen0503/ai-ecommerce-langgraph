"""Admin dashboard API: list refund requests waiting on a human, and let the
admin approve/reject them -- which resumes the paused LangGraph run.
"""
from langchain_core.messages import AIMessage
from langgraph.types import Command
from fastapi import APIRouter, HTTPException

from app_reference.agent.graph import get_graph
from app_reference.database import SessionLocal
from app_reference.models import PendingApproval, SentEmail
from app_reference.schemas import DecisionRequest, PendingApprovalOut, SentEmailOut

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/pending-approvals", response_model=list[PendingApprovalOut])
def list_pending_approvals(status: str | None = None):
    db = SessionLocal()
    try:
        query = db.query(PendingApproval)
        if status:
            query = query.filter(PendingApproval.status == status)
        return query.order_by(PendingApproval.created_at.desc()).all()
    finally:
        db.close()


@router.post("/approvals/{approval_id}/decision")
def decide_approval(approval_id: str, payload: DecisionRequest):
    db = SessionLocal()
    try:
        row = db.query(PendingApproval).filter(PendingApproval.id == approval_id).first()
        if not row:
            raise HTTPException(status_code=404, detail="Approval request not found")
        if row.status != "pending":
            raise HTTPException(status_code=409, detail=f"Already decided ({row.status})")
        session_id = row.session_id
        row.decided_by = payload.decided_by
        row.admin_note = payload.note
        db.commit()
    finally:
        db.close()

    # Resume the paused graph run: this re-enters `wait_for_decision`, which
    # picks up `payload.decision` as the interrupt()'s return value, then
    # continues on to `finalize` (mocked email) and `respond` (LLM reply).
    graph = get_graph()
    config = {"configurable": {"thread_id": session_id}}
    result = graph.invoke(Command(resume={"decision": payload.decision}), config=config)

    messages = result.get("messages", [])
    final_reply = messages[-1].content if messages and isinstance(messages[-1], AIMessage) else None

    return {
        "approval_id": approval_id,
        "decision": payload.decision,
        "session_id": session_id,
        "final_customer_message": final_reply,
    }


@router.get("/emails", response_model=list[SentEmailOut])
def list_sent_emails():
    db = SessionLocal()
    try:
        return db.query(SentEmail).order_by(SentEmail.created_at.desc()).all()
    finally:
        db.close()
