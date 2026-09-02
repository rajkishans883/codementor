from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.coding_session import CodingSession
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.problem import Problem

from app.schemas.chat import MessageCreate, MessageResponse, ChatResponse
from app.middleware.auth import get_current_user

from app.services.ai_service import ai_service


router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.post(
    "/sessions/{session_id}/message",
    response_model=ChatResponse
)
def send_message(
    session_id: int,
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message in a coding session chat."""

    # ============================================================
    # 1. Get the coding session
    # ============================================================

    session = db.query(CodingSession).filter(
        CodingSession.id == session_id,
        CodingSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    # ============================================================
    # 2. Get the problem associated with this session
    # ============================================================

    problem = db.query(Problem).filter(
        Problem.id == session.problem_id
    ).first()

    if not problem:
        raise HTTPException(
            status_code=404,
            detail="Problem not found"
        )

    # ============================================================
    # 3. Get or create conversation
    # ============================================================

    conversation = db.query(Conversation).filter(
        Conversation.coding_session_id == session_id
    ).first()

    if not conversation:

        conversation = Conversation(
            coding_session_id=session_id,
            user_id=current_user.id,
            title=f"Chat for session {session_id}"
        )

        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    # ============================================================
    # 4. Get previous conversation history
    # ============================================================

    previous_messages = db.query(Message).filter(
        Message.conversation_id == conversation.id
    ).order_by(
        Message.created_at.asc()
    ).all()

    conversation_history = []

    for msg in previous_messages:

        conversation_history.append({
            "role": msg.role,
            "content": msg.content
        })

    # ============================================================
    # 5. Save user's message
    # ============================================================

    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=message_data.content
    )

    db.add(user_message)
    db.commit()
    db.refresh(user_message)

    # ============================================================
    # 6. Prepare problem information
    # ============================================================

    problem_data = {
        "title": problem.title,
        "description": problem.description,
        "difficulty": problem.difficulty,
        "constraints": problem.constraints,
        "examples": problem.examples
    }

    # ============================================================
    # 7. Call Mistral through AIService
    # ============================================================

    try:

        ai_reply = ai_service.chat(
            problem=problem_data,
            current_code=session.current_code or "",
            language=session.language or "python",
            conversation_history=conversation_history,
            user_message=message_data.content
        )

    except Exception as e:

        # Roll back any pending database transaction
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"AI service error: {str(e)}"
        )

    # ============================================================
    # 8. Save AI response
    # ============================================================

    ai_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=ai_reply
    )

    db.add(ai_message)
    db.commit()
    db.refresh(ai_message)

    # ============================================================
    # 9. Return both messages
    # ============================================================

    return {
        "user_message": user_message,
        "ai_message": ai_message
    }


@router.get(
    "/sessions/{session_id}/history",
    response_model=list[MessageResponse]
)
def get_chat_history(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get chat history of a coding session."""

    # ============================================================
    # 1. Verify session belongs to current user
    # ============================================================

    session = db.query(CodingSession).filter(
        CodingSession.id == session_id,
        CodingSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    # ============================================================
    # 2. Get conversation
    # ============================================================

    conversation = db.query(Conversation).filter(
        Conversation.coding_session_id == session_id
    ).first()

    if not conversation:
        return []

    # ============================================================
    # 3. Get messages
    # ============================================================

    messages = db.query(Message).filter(
        Message.conversation_id == conversation.id
    ).order_by(
        Message.created_at.asc()
    ).all()

    return messages