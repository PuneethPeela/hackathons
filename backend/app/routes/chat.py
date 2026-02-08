"""Chat routes"""
from flask import Blueprint, request, jsonify
from ..middleware.jwt_middleware import jwt_required_with_user, get_current_user
from ..middleware.audit_logger import log_audit
from ..services.ai_service import AIService
from ..services.conversation_service import ConversationService
from ..services.medical_knowledge_service import MedicalKnowledgeService
from ..services.medical_nlp_service import MedicalNLPService
import time

bp = Blueprint('chat', __name__)
ai_service = AIService()


@bp.route('/message', methods=['POST'])
@jwt_required_with_user
def send_message():
    """
    Send chat message endpoint
    
    Request body:
    {
        "message": "user message",
        "conversation_id": "optional conversation ID"
    }
    
    Returns:
        AI response with conversation details
    """
    try:
        current_user = get_current_user()
        data = request.get_json()
        
        # Validate input
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400
        
        user_message = data['message'].strip()
        
        if not user_message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        if len(user_message) > 1000:
            return jsonify({'error': 'Message too long (max 1000 characters)'}), 400
        
        conversation_id = data.get('conversation_id')
        
        # Start timing for 3-second requirement
        start_time = time.time()
        
        # Check for emergency
        if ai_service.check_for_emergency(user_message):
            emergency_response = ai_service.get_emergency_response()
            
            # Still log the conversation
            if not conversation_id:
                conversation = ConversationService.create_conversation(
                    user_id=current_user.id,
                    title="Emergency Alert"
                )
                conversation_id = conversation.id
            
            # Save messages
            ConversationService.add_message(
                conversation_id=conversation_id,
                role='user',
                content=user_message
            )
            
            ConversationService.add_message(
                conversation_id=conversation_id,
                role='assistant',
                content=emergency_response,
                metadata={'emergency': True}
            )
            
            # Audit log
            log_audit(
                user_id=current_user.id,
                action='emergency_detected',
                resource_type='conversation',
                resource_id=conversation_id,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent'),
                success=True
            )
            
            return jsonify({
                'response': emergency_response,
                'conversation_id': conversation_id,
                'emergency': True,
                'response_time': time.time() - start_time
            }), 200
        
        # Create or get conversation
        if conversation_id:
            conversation = ConversationService.get_conversation(
                conversation_id=conversation_id,
                user_id=current_user.id
            )
            
            if not conversation:
                return jsonify({'error': 'Conversation not found'}), 404
        else:
            # Create new conversation
            conversation = ConversationService.create_conversation(
                user_id=current_user.id,
                title=user_message[:50]  # Use first 50 chars as title
            )
            conversation_id = conversation.id
        
        # Save user message
        ConversationService.add_message(
            conversation_id=conversation_id,
            role='user',
            content=user_message
        )
        
        # Get conversation context (last 10 messages)
        conversation_context = ConversationService.get_conversation_context(
            conversation_id=conversation_id,
            max_messages=10
        )
        
        # Get relevant medical knowledge
        medical_context = MedicalKnowledgeService.get_relevant_context_for_query(
            user_message
        )
        
        # Generate AI response
        ai_result = ai_service.generate_chat_response(
            user_message=user_message,
            conversation_history=conversation_context,
            medical_context=medical_context if medical_context else None
        )
        
        ai_response = ai_result['response']
        
        # Simplify medical terminology if needed
        readability = MedicalNLPService.calculate_readability(ai_response)
        if not readability.get('is_easy_to_read'):
            ai_response = MedicalNLPService.improve_readability(ai_response)
        
        # Save AI response
        ConversationService.add_message(
            conversation_id=conversation_id,
            role='assistant',
            content=ai_response,
            metadata={
                'tokens_used': ai_result.get('tokens_used'),
                'model': ai_result.get('model'),
                'response_time': ai_result.get('response_time'),
                'readability_score': readability.get('flesch_reading_ease')
            }
        )
        
        # Calculate total response time
        total_time = time.time() - start_time
        
        # Audit log
        log_audit(
            user_id=current_user.id,
            action='send_chat_message',
            resource_type='conversation',
            resource_id=conversation_id,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            details={
                'message_length': len(user_message),
                'response_time': total_time,
                'tokens_used': ai_result.get('tokens_used')
            },
            success=True
        )
        
        # Check if response time meets requirement (3 seconds)
        if total_time > 3.0:
            # Log warning but still return response
            print(f"Warning: Response time {total_time:.2f}s exceeds 3s requirement")
        
        return jsonify({
            'response': ai_response,
            'conversation_id': conversation_id,
            'response_time': round(total_time, 3),
            'tokens_used': ai_result.get('tokens_used'),
            'readability': {
                'score': readability.get('flesch_reading_ease'),
                'level': readability.get('readability_level'),
                'is_easy': readability.get('is_easy_to_read')
            }
        }), 200
        
    except Exception as e:
        # Audit log failure
        log_audit(
            user_id=current_user.id if current_user else None,
            action='send_chat_message',
            resource_type='conversation',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            details={'error': str(e)},
            success=False
        )
        
        return jsonify({'error': f'Error processing message: {str(e)}'}), 500


@bp.route('/history/<conversation_id>', methods=['GET'])
@jwt_required_with_user
def get_history(conversation_id):
    """
    Get conversation history endpoint
    
    Returns:
        All messages in the conversation
    """
    try:
        current_user = get_current_user()
        
        # Verify conversation belongs to user
        conversation = ConversationService.get_conversation(
            conversation_id=conversation_id,
            user_id=current_user.id
        )
        
        if not conversation:
            return jsonify({'error': 'Conversation not found'}), 404
        
        # Get all messages
        messages = ConversationService.get_conversation_messages(
            conversation_id=conversation_id
        )
        
        # Format messages
        formatted_messages = [
            {
                'id': msg.id,
                'role': msg.role,
                'content': msg.content,
                'created_at': msg.created_at.isoformat(),
                'metadata': msg.metadata
            }
            for msg in messages
        ]
        
        # Audit log
        log_audit(
            user_id=current_user.id,
            action='view_conversation_history',
            resource_type='conversation',
            resource_id=conversation_id,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            success=True
        )
        
        return jsonify({
            'conversation_id': conversation_id,
            'title': conversation.title,
            'created_at': conversation.created_at.isoformat(),
            'updated_at': conversation.updated_at.isoformat(),
            'message_count': len(formatted_messages),
            'messages': formatted_messages
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error retrieving history: {str(e)}'}), 500


@bp.route('/conversations', methods=['GET'])
@jwt_required_with_user
def get_conversations():
    """
    Get all conversations for current user
    
    Query params:
        limit: Max conversations (default 20)
        offset: Offset for pagination (default 0)
    
    Returns:
        List of conversations
    """
    try:
        current_user = get_current_user()
        
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Validate limits
        if limit > 100:
            limit = 100
        if limit < 1:
            limit = 20
        
        # Get conversations
        conversations = ConversationService.get_user_conversations(
            user_id=current_user.id,
            limit=limit,
            offset=offset
        )
        
        # Format conversations with summaries
        formatted_conversations = []
        for conv in conversations:
            summary = ConversationService.get_conversation_summary(conv.id)
            formatted_conversations.append(summary)
        
        return jsonify({
            'conversations': formatted_conversations,
            'count': len(formatted_conversations),
            'limit': limit,
            'offset': offset
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error retrieving conversations: {str(e)}'}), 500


@bp.route('/conversations/<conversation_id>', methods=['DELETE'])
@jwt_required_with_user
def delete_conversation(conversation_id):
    """
    Delete a conversation
    
    Returns:
        Success message
    """
    try:
        current_user = get_current_user()
        
        # Delete conversation
        success = ConversationService.delete_conversation(
            conversation_id=conversation_id,
            user_id=current_user.id
        )
        
        if not success:
            return jsonify({'error': 'Conversation not found'}), 404
        
        # Audit log
        log_audit(
            user_id=current_user.id,
            action='delete_conversation',
            resource_type='conversation',
            resource_id=conversation_id,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            success=True
        )
        
        return jsonify({'message': 'Conversation deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': f'Error deleting conversation: {str(e)}'}), 500
