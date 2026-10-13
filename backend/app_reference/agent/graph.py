"""The LangGraph StateGraph: lookup -> eligibility check -> human-in-the-loop
approval gate -> finalize/email, with an LLM used only to extract intent and
to phrase the final reply.

::

    START -> extract_intent -+-> respond -> END                       (no order id yet)
                              +-> lookup_order -+-> respond -> END     (order not found / just a status question)
                                                 +-> check_eligibility -+-> respond -> END   (outside 14-day window)
                                                                        +-> approval_gate -+-> finalize -> respond -> END        (<=100 EUR, auto-approved)
                                                                                            +-> escalate_for_approval -> wait_for_decision -> finalize -> respond -> END
                                                                                                                         ^^^^^^^^^^^^^^^^^^
                                                                                                                         graph PAUSES here (interrupt) until an
                                                                                                                         admin calls Command(resume=...)
"""
import sqlite3

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph

from app_reference.agent import nodes
from app_reference.agent.state import AgentState
from app_reference.config import get_settings

settings = get_settings()

_graph = None
_checkpointer = None
_conn = None


def build_graph(checkpointer) -> "CompiledGraph":  # noqa: F821
    graph = StateGraph(AgentState)

    graph.add_node("extract_intent", nodes.extract_intent)
    graph.add_node("lookup_order", nodes.lookup_order)
    graph.add_node("check_eligibility", nodes.check_eligibility)
    graph.add_node("approval_gate", nodes.approval_gate)
    graph.add_node("escalate_for_approval", nodes.escalate_for_approval)
    graph.add_node("wait_for_decision", nodes.wait_for_decision)
    graph.add_node("finalize", nodes.finalize)
    graph.add_node("respond", nodes.respond)

    graph.add_edge(START, "extract_intent")
    graph.add_conditional_edges("extract_intent", nodes.route_after_extract)
    graph.add_conditional_edges("lookup_order", nodes.route_after_lookup)
    graph.add_conditional_edges("check_eligibility", nodes.route_after_eligibility)
    graph.add_conditional_edges("approval_gate", nodes.route_after_approval_gate)
    graph.add_edge("escalate_for_approval", "wait_for_decision")
    graph.add_edge("wait_for_decision", "finalize")
    graph.add_edge("finalize", "respond")
    graph.add_edge("respond", END)

    return graph.compile(checkpointer=checkpointer)


def get_graph():
    """Lazily builds a module-level singleton graph backed by a SQLite
    checkpointer, so interrupted conversations survive across separate HTTP
    requests (and process restarts) until an admin makes a decision."""
    global _graph, _checkpointer, _conn
    if _graph is None:
        _conn = sqlite3.connect(settings.checkpoint_db_path, check_same_thread=False)
        _checkpointer = SqliteSaver(_conn)
        _graph = build_graph(_checkpointer)
    return _graph
