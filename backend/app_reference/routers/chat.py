"""Customer-facing chat endpoint that drives the LangGraph agent."""
from langchain_core.messages import AIMessage, HumanMessage
from fastapi import APIRouter
from app_reference.agent.graph import get_graph
from app_reference.schemas import ChatMessageOut, ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["chat"])


def _messages_out(state_values: dict) -> list[ChatMessageOut]:
    out = []
    for m in state_values.get("messages", []):
        if isinstance(m, HumanMessage):
            out.append(ChatMessageOut(role="user", content=m.content))
        elif isinstance(m, AIMessage):
            out.append(ChatMessageOut(role="assistant", content=m.content))
    return out


@router.post("", response_model=ChatResponse)
def send_message(payload: ChatRequest):
    graph = get_graph()
    config = {"configurable": {"thread_id": payload.session_id}}

    snapshot = graph.get_state(config)
    is_awaiting_approval = bool(snapshot.next) and "wait_for_decision" in snapshot.next

    if is_awaiting_approval:
        return ChatResponse(
            session_id=payload.session_id,
            reply="Your previous refund request is still awaiting admin review -- you'll get an email as soon "
            "as it's decided. Feel free to ask me anything else in the meantime.",
            status="awaiting_approval",
            messages=_messages_out(snapshot.values),
        )

    result = graph.invoke(
        {"messages": [HumanMessage(content=payload.message)], "session_id": payload.session_id},
        config=config,
    )

    if "__interrupt__" in result:
        interrupt_info = result["__interrupt__"][0].value
        return ChatResponse(
            session_id=payload.session_id,
            reply=interrupt_info["message"]
            + " I've submitted it for approval and will let you know as soon as it's decided.",
            status="awaiting_approval",
            messages=_messages_out(graph.get_state(config).values),
        )

    messages = result.get("messages", [])
    reply = messages[-1].content if messages and isinstance(messages[-1], AIMessage) else "..."
    return ChatResponse(session_id=payload.session_id, reply=reply, status="ok", messages=_messages_out(result))


@router.get("/{session_id}/messages", response_model=list[ChatMessageOut])
def get_messages(session_id: str):
    graph = get_graph()
    config = {"configurable": {"thread_id": session_id}}
    snapshot = graph.get_state(config)
    return _messages_out(snapshot.values) if snapshot.values else []
