"""Shared state for the LangGraph customer-support graph."""
from typing import Annotated, Any, Optional, TypedDict

from langgraph.graph.message import add_messages


class AgentState(TypedDict, total=False):
    # Full chat history (LangGraph's add_messages reducer appends new messages)
    messages: Annotated[list, add_messages]

    # Conversation-level slots the graph fills in as it works through a request
    session_id: str
    order_id: Optional[str]
    order: Optional[dict[str, Any]]
    wants_return: bool
    refund_amount: Optional[float]

    eligibility: Optional[dict[str, Any]]  # {"eligible": bool, "days_since_delivery": int, "deadline": str, "reason": str}

    approval_status: Optional[str]  # None | "auto_approved" | "pending" | "approved" | "rejected"
    approval_id: Optional[str]  # PendingApproval row id, when escalated

    # Set by terminal nodes to short-circuit straight to the final LLM reply
    outcome_note: Optional[str]
