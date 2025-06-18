from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
import json

from ..database import get_db
from ..services.conversation_learning_service import ConversationLearningService
from ..models.conversation import ConversationSession, ConversationMessage, ConversationPattern

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

@router.get("/conversations")
async def get_conversation_analytics(
    days: int = 30,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get conversation analytics for learning insights"""
    
    learning_service = ConversationLearningService(db)
    
    try:
        analytics = await learning_service.get_conversation_analytics(days=days)
        return {
            "status": "success",
            "data": analytics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        learning_service.close()

@router.get("/patterns")
async def get_learned_patterns(
    project_type: str = None,
    min_confidence: float = 0.5,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get learned conversation patterns"""
    
    try:
        query = db.query(ConversationPattern).filter(
            ConversationPattern.confidence_score >= min_confidence
        )
        
        if project_type:
            query = query.filter(ConversationPattern.project_type == project_type)
        
        patterns = query.order_by(ConversationPattern.success_rate.desc()).limit(50).all()
        
        pattern_data = []
        for pattern in patterns:
            pattern_data.append({
                "pattern_name": pattern.pattern_name,
                "project_type": pattern.project_type,
                "success_rate": pattern.success_rate,
                "times_seen": pattern.times_seen,
                "confidence_score": pattern.confidence_score,
                "most_successful_followup": pattern.most_successful_followup,
                "sample_queries": pattern.get_sample_queries()[:3],
                "sample_responses": pattern.get_sample_responses()[:2],
                "last_updated": pattern.last_updated.isoformat() if pattern.last_updated else None
            })
        
        return {
            "status": "success",
            "patterns": pattern_data,
            "total_patterns": len(pattern_data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversations/recent")
async def get_recent_conversations(
    limit: int = 20,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get recent conversations for review"""
    
    try:
        sessions = db.query(ConversationSession).order_by(
            ConversationSession.started_at.desc()
        ).limit(limit).all()
        
        conversations = []
        for session in sessions:
            messages = db.query(ConversationMessage).filter(
                ConversationMessage.session_id == session.session_id
            ).order_by(ConversationMessage.message_order).all()
            
            conversation_data = {
                "session_id": session.session_id,
                "partner_id": session.partner_id,
                "agent_used": session.agent_used,
                "started_at": session.started_at.isoformat(),
                "total_messages": session.total_messages,
                "led_to_registration": session.led_to_registration,
                "messages": []
            }
            
            for msg in messages:
                conversation_data["messages"].append({
                    "order": msg.message_order,
                    "user_message": msg.user_message,
                    "agent_response": msg.agent_response[:100] + "..." if len(msg.agent_response) > 100 else msg.agent_response,
                    "ai_powered": msg.ai_powered,
                    "project_type_detected": msg.project_type_detected,
                    "led_to_pricing": msg.led_to_pricing,
                    "led_to_registration": msg.led_to_registration,
                    "user_responded": msg.user_responded
                })
            
            conversations.append(conversation_data)
        
        return {
            "status": "success", 
            "conversations": conversations
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ai-performance")
async def get_ai_performance_metrics(
    days: int = 7,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get AI performance metrics"""
    
    from datetime import datetime, timedelta
    
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Get AI vs non-AI message performance
        messages = db.query(ConversationMessage).filter(
            ConversationMessage.created_at >= cutoff_date
        ).all()
        
        ai_messages = [m for m in messages if m.ai_powered]
        non_ai_messages = [m for m in messages if not m.ai_powered]
        
        # Calculate success rates
        ai_success_rate = len([m for m in ai_messages if m.user_responded]) / len(ai_messages) if ai_messages else 0
        non_ai_success_rate = len([m for m in non_ai_messages if m.user_responded]) / len(non_ai_messages) if non_ai_messages else 0
        
        # Average response times
        ai_response_times = [m.user_response_time_seconds for m in ai_messages if m.user_response_time_seconds]
        non_ai_response_times = [m.user_response_time_seconds for m in non_ai_messages if m.user_response_time_seconds]
        
        avg_ai_response_time = sum(ai_response_times) / len(ai_response_times) if ai_response_times else 0
        avg_non_ai_response_time = sum(non_ai_response_times) / len(non_ai_response_times) if non_ai_response_times else 0
        
        return {
            "status": "success",
            "period_days": days,
            "ai_metrics": {
                "total_messages": len(ai_messages),
                "user_response_rate": ai_success_rate * 100,
                "avg_response_time_seconds": avg_ai_response_time,
                "led_to_pricing": len([m for m in ai_messages if m.led_to_pricing]),
                "led_to_registration": len([m for m in ai_messages if m.led_to_registration])
            },
            "non_ai_metrics": {
                "total_messages": len(non_ai_messages),
                "user_response_rate": non_ai_success_rate * 100,
                "avg_response_time_seconds": avg_non_ai_response_time,
                "led_to_pricing": len([m for m in non_ai_messages if m.led_to_pricing]),
                "led_to_registration": len([m for m in non_ai_messages if m.led_to_registration])
            },
            "improvement": {
                "response_rate_improvement": (ai_success_rate - non_ai_success_rate) * 100,
                "ai_performs_better": ai_success_rate > non_ai_success_rate
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/feedback")
async def submit_conversation_feedback(
    session_id: str,
    rating: int,  # 1-5 stars
    feedback: str = "",
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Submit feedback for a conversation (for future use)"""
    
    try:
        session = db.query(ConversationSession).filter(
            ConversationSession.session_id == session_id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session.user_satisfaction_score = rating
        db.commit()
        
        return {
            "status": "success",
            "message": "Feedback recorded"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))