from app.models.mental_health_conversation import MentalHealthConversation


def test_mental_health_conversation_model():
    conversation = MentalHealthConversation(
        question="How are you feeling?",
        answer="I'm feeling good.",
    )
    assert conversation.question == "How are you feeling?"
    assert conversation.answer == "I'm feeling good."
    assert conversation.created_at is None  # Will be set by database
    assert conversation.updated_at is None  # Will be set by database
