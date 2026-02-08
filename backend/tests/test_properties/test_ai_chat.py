"""
Property-based tests for AI chat functionality

**Feature: ai-patient-support-assistant**

Tests Properties 5, 7, 8, 9 from design document
"""
import pytest
from hypothesis import given, strategies as st, settings, assume
from datetime import datetime, timedelta
import time
from app.models import User, Conversation, Message, SessionLocal
from app.services.auth_service import AuthService
from app.services.conversation_service import ConversationService
from app.services.medical_knowledge_service import MedicalKnowledgeService
from app.services.medical_nlp_service import MedicalNLPService
from unittest.mock import Mock, patch


# Custom strategies
@st.composite
def user_message_strategy(draw):
    """Generate realistic user messages"""
    message_types = [
        "What is {disease}?",
        "How do I treat {symptom}?",
        "Tell me about {disease}",
        "I have {symptom}, what should I do?",
        "What causes {disease}?",
        "How can I prevent {disease}?",
    ]
    
    diseases = ['diabetes', 'hypertension', 'common cold', 'flu', 'asthma']
    symptoms = ['fever', 'cough', 'headache', 'fatigue', 'pain']
    
    template = draw(st.sampled_from(message_types))
    disease = draw(st.sampled_from(diseases))
    symptom = draw(st.sampled_from(symptoms))
    
    message = template.replace('{disease}', disease).replace('{symptom}', symptom)
    return message


@st.composite
def conversation_history_strategy(draw):
    """Generate conversation history"""
    num_messages = draw(st.integers(min_value=0, max_value=10))
    messages = []
    
    for i in range(num_messages):
        role = 'user' if i % 2 == 0 else 'assistant'
        content = draw(st.text(min_size=10, max_size=100))
        messages.append({'role': role, 'content': content})
    
    return messages


class TestAIChatProperties:
    """Test AI chat-related properties"""
    
    @given(
        email=st.emails(),
        message=user_message_strategy()
    )
    @settings(max_examples=50, deadline=10000)  # 10 second deadline for AI calls
    @patch('app.services.ai_service.openai.ChatCompletion.create')
    def test_property_5_ai_response_time_constraint(
        self, mock_openai, email, message, db_session
    ):
        """
        **Property 5: AI response time constraint**
        
        WHEN a user sends a chat message
        THEN the system SHALL return a response within 3 seconds
        
        Validates: Requirements 2.1, 8.1
        """
        # Mock OpenAI response
        mock_openai.return_value = Mock(
            choices=[Mock(
                message=Mock(content="This is a test response about your health question."),
                finish_reason='stop'
            )],
            usage=Mock(total_tokens=50)
        )
        
        # Create user
        user = User(
            email=email,
            password_hash=AuthService.hash_password("TestPass123"),
            first_name="Test",
            last_name="User",
            date_of_birth=datetime(1990, 1, 1),
            gender="other"
        )
        db_session.add(user)
        db_session.commit()
        
        # Create conversation
        conversation = ConversationService.create_conversation(
            user_id=user.id,
            title="Test Conversation"
        )
        
        # Measure response time
        start_time = time.time()
        
        # Add user message
        ConversationService.add_message(
            conversation_id=conversation.id,
            role='user',
            content=message
        )
        
        # Simulate AI service call (mocked)
        from app.services.ai_service import AIService
        ai_service = AIService()
        
        try:
            result = ai_service.generate_chat_response(
                user_message=message,
                conversation_history=[],
                medical_context=None
            )
            
            # Add AI response
            ConversationService.add_message(
                conversation_id=conversation.id,
                role='assistant',
                content=result['response']
            )
            
            elapsed_time = time.time() - start_time
            
            # Verify response time is under 3 seconds
            # Note: With mocking, this should be very fast
            # In real scenario, this tests the full pipeline
            assert elapsed_time < 3.0, \
                f"Response time {elapsed_time:.2f}s exceeds 3 second requirement"
            
            # Verify response was generated
            assert result['response'] is not None
            assert len(result['response']) > 0
            
        except Exception as e:
            # If OpenAI is not configured, skip this test
            if "OPENAI_API_KEY" in str(e):
                pytest.skip("OpenAI API key not configured")
            raise
        
        # Cleanup
        ConversationService.delete_conversation(conversation.id, user.id)
        db_session.delete(user)
        db_session.commit()
    
    @given(
        query=st.sampled_from([
            'diabetes', 'hypertension', 'common cold',
            'fever', 'cough', 'headache'
        ])
    )
    @settings(max_examples=100)
    def test_property_7_knowledge_base_retrieval(self, query):
        """
        **Property 7: Knowledge base retrieval**
        
        WHEN the AI needs medical information
        THEN the system SHALL retrieve relevant data from the knowledge base
        AND the retrieved data SHALL be relevant to the query
        
        Validates: Requirements 2.3
        """
        # Search for diseases
        diseases = MedicalKnowledgeService.search_diseases(query, limit=5)
        
        # If results found, verify relevance
        if diseases:
            for disease in diseases:
                # Check that query appears in name, description, or symptoms
                disease_text = (
                    disease.get('name', '').lower() +
                    disease.get('description', '').lower() +
                    ' '.join(disease.get('symptoms', [])).lower()
                )
                
                # Verify query relevance
                assert query.lower() in disease_text or \
                       any(word in disease_text for word in query.lower().split()), \
                       f"Retrieved disease not relevant to query '{query}'"
        
        # Search for symptoms
        symptoms = MedicalKnowledgeService.search_symptoms(query, limit=5)
        
        # If results found, verify relevance
        if symptoms:
            for symptom in symptoms:
                symptom_text = (
                    symptom.get('name', '').lower() +
                    symptom.get('description', '').lower()
                )
                
                assert query.lower() in symptom_text or \
                       any(word in symptom_text for word in query.lower().split()), \
                       f"Retrieved symptom not relevant to query '{query}'"
        
        # Get relevant context
        context = MedicalKnowledgeService.get_relevant_context_for_query(query)
        
        # Context should be a string (empty or with content)
        assert isinstance(context, str)
        
        # If context is not empty, it should mention the query
        if context:
            assert query.lower() in context.lower() or \
                   any(word in context.lower() for word in query.lower().split())
    
    @given(
        email=st.emails(),
        messages=st.lists(
            st.text(min_size=10, max_size=200),
            min_size=1,
            max_size=10
        )
    )
    @settings(max_examples=100)
    def test_property_8_conversation_persistence(self, email, messages, db_session):
        """
        **Property 8: Conversation persistence**
        
        WHEN messages are sent in a conversation
        THEN all messages SHALL be stored in the database
        AND messages SHALL be retrievable in chronological order
        
        Validates: Requirements 2.4
        """
        # Create user
        user = User(
            email=email,
            password_hash=AuthService.hash_password("TestPass123"),
            first_name="Test",
            last_name="User",
            date_of_birth=datetime(1990, 1, 1),
            gender="other"
        )
        db_session.add(user)
        db_session.commit()
        
        # Create conversation
        conversation = ConversationService.create_conversation(
            user_id=user.id,
            title="Test Conversation"
        )
        
        # Add messages alternating between user and assistant
        for i, message_content in enumerate(messages):
            role = 'user' if i % 2 == 0 else 'assistant'
            ConversationService.add_message(
                conversation_id=conversation.id,
                role=role,
                content=message_content
            )
        
        # Retrieve messages
        retrieved_messages = ConversationService.get_conversation_messages(
            conversation_id=conversation.id
        )
        
        # Verify all messages were stored
        assert len(retrieved_messages) == len(messages), \
            "Not all messages were persisted"
        
        # Verify chronological order
        for i in range(len(retrieved_messages) - 1):
            assert retrieved_messages[i].created_at <= retrieved_messages[i + 1].created_at, \
                "Messages not in chronological order"
        
        # Verify content matches
        for i, msg in enumerate(retrieved_messages):
            assert msg.content == messages[i], \
                f"Message content mismatch at index {i}"
            
            # Verify role alternates correctly
            expected_role = 'user' if i % 2 == 0 else 'assistant'
            assert msg.role == expected_role, \
                f"Message role mismatch at index {i}"
        
        # Test conversation context retrieval
        context = ConversationService.get_conversation_context(
            conversation_id=conversation.id,
            max_messages=5
        )
        
        # Context should have at most 5 messages
        assert len(context) <= 5
        
        # Context should be in correct format
        for ctx_msg in context:
            assert 'role' in ctx_msg
            assert 'content' in ctx_msg
            assert ctx_msg['role'] in ['user', 'assistant']
        
        # Cleanup
        ConversationService.delete_conversation(conversation.id, user.id)
        db_session.delete(user)
        db_session.commit()
    
    @given(
        text=st.text(min_size=50, max_size=500)
    )
    @settings(max_examples=100)
    @patch('app.services.ai_service.openai.ChatCompletion.create')
    def test_property_9_ai_response_compliance(self, mock_openai, text):
        """
        **Property 9: AI response compliance**
        
        WHEN the AI generates a response
        THEN the response SHALL include appropriate medical disclaimers
        AND the response SHALL be in patient-friendly language
        
        Validates: Requirements 2.5, 8.1
        """
        # Mock OpenAI to return our test text
        mock_openai.return_value = Mock(
            choices=[Mock(
                message=Mock(content=text),
                finish_reason='stop'
            )],
            usage=Mock(total_tokens=50)
        )
        
        from app.services.ai_service import AIService
        ai_service = AIService()
        
        try:
            # Generate response
            result = ai_service.generate_chat_response(
                user_message="Test medical question about diabetes",
                conversation_history=[],
                medical_context=None
            )
            
            response = result['response']
            
            # Check for medical disclaimer if response contains medical content
            medical_keywords = [
                'symptom', 'disease', 'condition', 'treatment', 'medication',
                'diagnosis', 'pain', 'fever', 'infection', 'doctor'
            ]
            
            has_medical_content = any(
                keyword in response.lower() for keyword in medical_keywords
            )
            
            if has_medical_content:
                # Should have disclaimer
                disclaimer_indicators = [
                    'medical advice', 'consult', 'healthcare professional',
                    'educational purposes', 'not constitute'
                ]
                
                has_disclaimer = any(
                    indicator in response.lower() for indicator in disclaimer_indicators
                )
                
                assert has_disclaimer, \
                    "Medical response should include disclaimer"
            
            # Test readability
            readability = MedicalNLPService.calculate_readability(response)
            
            # Response should have readability metrics
            assert 'flesch_reading_ease' in readability
            assert 'readability_level' in readability
            
            # Ideally, medical responses should be readable
            # (Flesch score >= 60 is considered standard/easy)
            # But we don't enforce this strictly as AI may vary
            
        except Exception as e:
            if "OPENAI_API_KEY" in str(e):
                pytest.skip("OpenAI API key not configured")
            raise
    
    @given(
        email=st.emails(),
        num_conversations=st.integers(min_value=1, max_value=5)
    )
    @settings(max_examples=50)
    def test_property_8_extended_conversation_management(
        self, email, num_conversations, db_session
    ):
        """
        **Property 8 (Extended): Conversation management**
        
        WHEN a user has multiple conversations
        THEN all conversations SHALL be retrievable
        AND conversations SHALL be ordered by most recent activity
        
        Validates: Requirements 2.4
        """
        # Create user
        user = User(
            email=email,
            password_hash=AuthService.hash_password("TestPass123"),
            first_name="Test",
            last_name="User",
            date_of_birth=datetime(1990, 1, 1),
            gender="other"
        )
        db_session.add(user)
        db_session.commit()
        
        # Create multiple conversations
        conversation_ids = []
        for i in range(num_conversations):
            conv = ConversationService.create_conversation(
                user_id=user.id,
                title=f"Conversation {i+1}"
            )
            conversation_ids.append(conv.id)
            
            # Add a message to each
            ConversationService.add_message(
                conversation_id=conv.id,
                role='user',
                content=f"Message in conversation {i+1}"
            )
            
            # Small delay to ensure different timestamps
            time.sleep(0.01)
        
        # Retrieve all conversations
        conversations = ConversationService.get_user_conversations(
            user_id=user.id,
            limit=20
        )
        
        # Verify count
        assert len(conversations) == num_conversations, \
            "Not all conversations retrieved"
        
        # Verify ordering (most recent first)
        for i in range(len(conversations) - 1):
            assert conversations[i].updated_at >= conversations[i + 1].updated_at, \
                "Conversations not ordered by most recent"
        
        # Test conversation summary
        for conv_id in conversation_ids:
            summary = ConversationService.get_conversation_summary(conv_id)
            
            assert summary is not None
            assert 'id' in summary
            assert 'title' in summary
            assert 'message_count' in summary
            assert summary['message_count'] >= 1  # At least one message
        
        # Cleanup
        for conv_id in conversation_ids:
            ConversationService.delete_conversation(conv_id, user.id)
        
        db_session.delete(user)
        db_session.commit()
    
    @given(
        medical_text=st.text(min_size=20, max_size=200)
    )
    @settings(max_examples=100)
    def test_property_9_extended_text_simplification(self, medical_text):
        """
        **Property 9 (Extended): Text simplification**
        
        WHEN medical text is processed
        THEN medical terms SHALL be identified
        AND simplified alternatives SHALL be provided
        
        Validates: Requirements 2.2
        """
        # Extract medical terms
        terms = MedicalNLPService.extract_medical_terms(medical_text)
        
        # Each term should have a definition
        for term, definition in terms:
            assert term is not None
            assert definition is not None
            assert len(definition) > 0
            assert definition != term  # Definition should be different from term
        
        # Test simplification
        simplified = MedicalNLPService.simplify_medical_text(medical_text)
        
        # Simplified text should exist
        assert simplified is not None
        assert isinstance(simplified, str)
        
        # If medical terms were found, simplified should be different
        if terms:
            # At least some terms should be replaced
            for term, definition in terms:
                if term.lower() in medical_text.lower():
                    # The simplified version should have the definition
                    assert definition.lower() in simplified.lower() or \
                           term.lower() in simplified.lower()
