"""
Conversation Service for managing chat context and history
"""
from typing import List, Dict, Optional
from datetime import datetime
from ..models import Conversation, Message, SessionLocal
from sqlalchemy import desc


class ConversationService:
    """Service for managing conversations and message history"""
    
    @staticmethod
    def create_conversation(user_id: str, title: Optional[str] = None) -> Conversation:
        """
        Create a new conversation
        
        Args:
            user_id: User ID
            title: Optional conversation title
        
        Returns:
            Created conversation
        """
        db = SessionLocal()
        
        try:
            conversation = Conversation(
                user_id=user_id,
                title=title or f"Conversation {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
            )
            
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
            
            return conversation
            
        except Exception as e:
            db.rollback()
            raise Exception(f"Error creating conversation: {str(e)}")
        finally:
            db.close()
    
    @staticmethod
    def get_conversation(conversation_id: str, user_id: str) -> Optional[Conversation]:
        """
        Get conversation by ID
        
        Args:
            conversation_id: Conversation ID
            user_id: User ID (for authorization)
        
        Returns:
            Conversation or None
        """
        db = SessionLocal()
        
        try:
            conversation = db.query(Conversation).filter(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            ).first()
            
            return conversation
            
        finally:
            db.close()
    
    @staticmethod
    def get_user_conversations(
        user_id: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[Conversation]:
        """
        Get all conversations for a user
        
        Args:
            user_id: User ID
            limit: Maximum number of conversations
            offset: Offset for pagination
        
        Returns:
            List of conversations
        """
        db = SessionLocal()
        
        try:
            conversations = db.query(Conversation).filter(
                Conversation.user_id == user_id
            ).order_by(
                desc(Conversation.updated_at)
            ).limit(limit).offset(offset).all()
            
            return conversations
            
        finally:
            db.close()
    
    @staticmethod
    def add_message(
        conversation_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict] = None
    ) -> Message:
        """
        Add message to conversation
        
        Args:
            conversation_id: Conversation ID
            role: Message role ('user' or 'assistant')
            content: Message content
            metadata: Optional metadata (tokens, response time, etc.)
        
        Returns:
            Created message
        """
        db = SessionLocal()
        
        try:
            message = Message(
                conversation_id=conversation_id,
                role=role,
                content=content,
                metadata=metadata
            )
            
            db.add(message)
            
            # Update conversation's updated_at timestamp
            conversation = db.query(Conversation).filter(
                Conversation.id == conversation_id
            ).first()
            
            if conversation:
                conversation.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(message)
            
            return message
            
        except Exception as e:
            db.rollback()
            raise Exception(f"Error adding message: {str(e)}")
        finally:
            db.close()
    
    @staticmethod
    def get_conversation_messages(
        conversation_id: str,
        limit: Optional[int] = None
    ) -> List[Message]:
        """
        Get messages for a conversation
        
        Args:
            conversation_id: Conversation ID
            limit: Optional limit (for context window)
        
        Returns:
            List of messages ordered by timestamp
        """
        db = SessionLocal()
        
        try:
            query = db.query(Message).filter(
                Message.conversation_id == conversation_id
            ).order_by(Message.created_at)
            
            if limit:
                # Get most recent messages
                query = query.limit(limit)
            
            messages = query.all()
            
            return messages
            
        finally:
            db.close()
    
    @staticmethod
    def get_conversation_context(
        conversation_id: str,
        max_messages: int = 10
    ) -> List[Dict[str, str]]:
        """
        Get conversation context for AI (recent messages)
        
        Args:
            conversation_id: Conversation ID
            max_messages: Maximum number of messages to include
        
        Returns:
            List of message dicts with role and content
        """
        db = SessionLocal()
        
        try:
            # Get recent messages
            messages = db.query(Message).filter(
                Message.conversation_id == conversation_id
            ).order_by(
                desc(Message.created_at)
            ).limit(max_messages).all()
            
            # Reverse to chronological order
            messages = list(reversed(messages))
            
            # Format for AI context
            context = [
                {
                    'role': msg.role,
                    'content': msg.content
                }
                for msg in messages
            ]
            
            return context
            
        finally:
            db.close()
    
    @staticmethod
    def update_conversation_title(
        conversation_id: str,
        user_id: str,
        title: str
    ) -> bool:
        """
        Update conversation title
        
        Args:
            conversation_id: Conversation ID
            user_id: User ID (for authorization)
            title: New title
        
        Returns:
            True if updated successfully
        """
        db = SessionLocal()
        
        try:
            conversation = db.query(Conversation).filter(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            ).first()
            
            if not conversation:
                return False
            
            conversation.title = title
            conversation.updated_at = datetime.utcnow()
            
            db.commit()
            return True
            
        except Exception as e:
            db.rollback()
            raise Exception(f"Error updating conversation title: {str(e)}")
        finally:
            db.close()
    
    @staticmethod
    def delete_conversation(conversation_id: str, user_id: str) -> bool:
        """
        Delete conversation and all its messages
        
        Args:
            conversation_id: Conversation ID
            user_id: User ID (for authorization)
        
        Returns:
            True if deleted successfully
        """
        db = SessionLocal()
        
        try:
            conversation = db.query(Conversation).filter(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            ).first()
            
            if not conversation:
                return False
            
            # Delete all messages (cascade should handle this, but explicit is better)
            db.query(Message).filter(
                Message.conversation_id == conversation_id
            ).delete()
            
            # Delete conversation
            db.delete(conversation)
            db.commit()
            
            return True
            
        except Exception as e:
            db.rollback()
            raise Exception(f"Error deleting conversation: {str(e)}")
        finally:
            db.close()
    
    @staticmethod
    def get_conversation_summary(conversation_id: str) -> Dict:
        """
        Get conversation summary (message count, last message time, etc.)
        
        Args:
            conversation_id: Conversation ID
        
        Returns:
            Summary dict
        """
        db = SessionLocal()
        
        try:
            conversation = db.query(Conversation).filter(
                Conversation.id == conversation_id
            ).first()
            
            if not conversation:
                return None
            
            message_count = db.query(Message).filter(
                Message.conversation_id == conversation_id
            ).count()
            
            last_message = db.query(Message).filter(
                Message.conversation_id == conversation_id
            ).order_by(desc(Message.created_at)).first()
            
            return {
                'id': conversation.id,
                'title': conversation.title,
                'message_count': message_count,
                'created_at': conversation.created_at.isoformat(),
                'updated_at': conversation.updated_at.isoformat(),
                'last_message': last_message.content[:100] if last_message else None,
                'last_message_time': last_message.created_at.isoformat() if last_message else None
            }
            
        finally:
            db.close()
