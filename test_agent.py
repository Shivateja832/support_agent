"""
Unit tests for CloudSync AI Support Agent
Tests persona detection, RAG retrieval, escalation logic,
sentiment analysis, confidence scoring, and feedback.
"""

import pytest
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent import (
    SupportAgent,
    detect_persona,
    should_escalate,
    load_all_documents,
    SentimentAnalyzer,
    ConfidenceScorer,
    ConversationMemory,
    EscalationChecker,
    PersonaDetector,
    PERSONA_LABELS,
)


# ─────────────────────────────────────────────
#  Persona Detection Tests
# ─────────────────────────────────────────────

class TestPersonaDetection:
    """Test persona classification logic"""

    def test_technical_expert_keywords(self):
        query = "How do I debug OAuth 2.0 authentication errors? I'm getting 401 and 403 errors."
        persona, confidence, _ = detect_persona(query)
        assert persona == "technical_expert"
        assert confidence >= 0.60

    def test_frustrated_user_keywords(self):
        query = "I've been trying to reset my password for HOURS and it's STILL not working!!! This is ridiculous!"
        persona, confidence, _ = detect_persona(query)
        assert persona == "frustrated_user"
        assert confidence >= 0.60

    def test_business_executive_keywords(self):
        query = "What's the SLA commitment for our Business plan? Our team is experiencing downtime and needs to know the business impact."
        persona, confidence, _ = detect_persona(query)
        assert persona == "business_exec"
        assert confidence >= 0.60

    def test_ambiguous_query_has_reasonable_confidence(self):
        query = "How is everything?"
        persona, confidence, _ = detect_persona(query)
        assert persona in ["technical_expert", "frustrated_user", "business_exec"]
        assert 0.0 <= confidence <= 1.0

    def test_empty_query_defaults_to_reasonable_persona(self):
        query = ""
        persona, confidence, _ = detect_persona(query)
        assert persona in ["technical_expert", "frustrated_user", "business_exec"]

    def test_api_query_is_technical(self):
        query = "Can you provide the API endpoint configuration and webhook payload structure?"
        persona, confidence, _ = detect_persona(query)
        assert persona == "technical_expert"

    def test_roi_sla_is_executive(self):
        query = "What is the ROI impact of this outage? When will operations resume?"
        persona, confidence, _ = detect_persona(query)
        assert persona == "business_exec"

    def test_persona_labels_exist(self):
        for key in ["technical_expert", "frustrated_user", "business_exec"]:
            assert key in PERSONA_LABELS
            assert len(PERSONA_LABELS[key]) > 0

    def test_detect_persona_returns_tuple(self):
        result = detect_persona("test message")
        assert isinstance(result, tuple)
        assert len(result) == 3

    def test_confidence_in_range(self):
        for query in ["API error", "I'm angry", "What is the business impact?"]:
            _, confidence, _ = detect_persona(query)
            assert 0.0 <= confidence <= 1.0, f"Confidence out of range for: {query}"


# ─────────────────────────────────────────────
#  Escalation Logic Tests
# ─────────────────────────────────────────────

class TestEscalationLogic:
    """Test escalation detection"""

    def test_sensitive_keywords_trigger_escalation(self):
        query = "Someone has fraudulently charged my account multiple times!"
        result, reason = should_escalate(
            query=query, retrieved_docs=[], low_conf_count=0,
            dissatisfaction_count=0, turn_count=1
        )
        assert result is True
        assert len(reason) > 0

    def test_no_docs_triggers_escalation(self):
        query = "Tell me about the Klingon integration"
        result, reason = should_escalate(
            query=query, retrieved_docs=[], low_conf_count=0,
            dissatisfaction_count=0, turn_count=2
        )
        assert result is True
        assert "no relevant" in reason.lower() or "knowledge" in reason.lower()

    def test_normal_query_no_escalation(self):
        query = "How do I reset my password?"
        result, reason = should_escalate(
            query=query, retrieved_docs=[{"score": 0.85}],
            low_conf_count=0, dissatisfaction_count=0, turn_count=1
        )
        assert result is False

    def test_repeated_dissatisfaction_triggers_escalation(self):
        query = "Your system still isn't working!"
        result, reason = should_escalate(
            query=query, retrieved_docs=[{"score": 0.5}],
            low_conf_count=1, dissatisfaction_count=2, turn_count=3
        )
        assert result is True

    def test_long_conversation_triggers_escalation(self):
        query = "Still not resolved"
        result, reason = should_escalate(
            query=query, retrieved_docs=[{"score": 0.4}],
            low_conf_count=3, dissatisfaction_count=1, turn_count=7
        )
        assert result is True

    def test_low_retrieval_confidence_triggers_escalation(self):
        query = "What is the answer?"
        result, reason = should_escalate(
            query=query, retrieved_docs=[{"score": 0.10}],
            low_conf_count=0, dissatisfaction_count=0, turn_count=1
        )
        assert result is True

    def test_legal_keywords(self):
        for kw in ["lawsuit", "attorney", "sue", "fraud"]:
            result, reason = should_escalate(
                query=f"I want to {kw} your company",
                retrieved_docs=[{"score": 0.9}],
                low_conf_count=0, dissatisfaction_count=0, turn_count=1
            )
            assert result is True, f"Should escalate for keyword: {kw}"

    def test_escalation_checker_configurable(self):
        checker = EscalationChecker(max_turns=3, low_score_limit=2)
        # Should escalate at turn 3
        result, _ = checker.should_escalate(
            message="help", retrieval_hits=[{"score": 0.5}],
            turn_count=3, low_confidence_count=0, persona="frustrated_user",
            dissatisfied_count=0
        )
        assert result is True

    def test_returns_tuple(self):
        result = should_escalate("test", [], 0, 0, 1)
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], bool)
        assert isinstance(result[1], str)


# ─────────────────────────────────────────────
#  Sentiment Analysis Tests
# ─────────────────────────────────────────────

class TestSentimentAnalysis:
    """Test sentiment analyzer"""

    def setup_method(self):
        self.analyzer = SentimentAnalyzer()

    def test_positive_sentiment(self):
        sentiment, score = self.analyzer.analyze("Thank you, this is great and works perfectly!")
        assert sentiment == "positive"
        assert score > 0

    def test_negative_sentiment(self):
        sentiment, score = self.analyzer.analyze("This is terrible! Nothing works and it's broken!!!")
        assert sentiment == "negative"
        assert score < 0

    def test_neutral_sentiment(self):
        sentiment, score = self.analyzer.analyze("when does my subscription renew")
        assert sentiment == "neutral"
        assert -0.3 <= score <= 0.3

    def test_score_in_range(self):
        for text in ["great!", "horrible failure", "just checking", "!!!!!!"]:
            _, score = self.analyzer.analyze(text)
            assert -1.0 <= score <= 1.0, f"Score out of range for: {text}"

    def test_get_label(self):
        assert "😊" in self.analyzer.get_label("positive")
        assert "😤" in self.analyzer.get_label("negative")
        assert "😐" in self.analyzer.get_label("neutral")

    def test_returns_tuple(self):
        result = self.analyzer.analyze("test message")
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_empty_string(self):
        sentiment, score = self.analyzer.analyze("")
        assert sentiment in ["positive", "negative", "neutral"]

    def test_caps_amplify_negativity(self):
        _, score_low = self.analyzer.analyze("terrible broken")
        _, score_caps = self.analyzer.analyze("TERRIBLE BROKEN!!")
        assert score_caps <= score_low  # More negative with caps


# ─────────────────────────────────────────────
#  Confidence Scorer Tests
# ─────────────────────────────────────────────

class TestConfidenceScorer:
    """Test confidence scoring"""

    def setup_method(self):
        self.scorer = ConfidenceScorer()

    def test_high_retrieval_gives_high_score(self):
        result = self.scorer.compute(
            retrieval_hits=[{"score": 0.9}, {"score": 0.85}],
            persona_confidence=0.9,
            response_text="Here are the detailed steps to resolve your issue. " * 5,
            sentiment_score=0.1,
        )
        assert result["overall"] >= 0.5
        assert result["label"] in ["High", "Medium"]

    def test_no_retrieval_gives_low_score(self):
        result = self.scorer.compute(
            retrieval_hits=[],
            persona_confidence=0.5,
            response_text="I cannot find information about this.",
            sentiment_score=0.0,
        )
        assert result["overall"] < 0.5

    def test_confidence_in_range(self):
        result = self.scorer.compute(
            retrieval_hits=[{"score": 0.6}],
            persona_confidence=0.7,
            response_text="Here is the answer.",
            sentiment_score=0.0,
        )
        assert 0.0 <= result["overall"] <= 1.0

    def test_returns_expected_keys(self):
        result = self.scorer.compute([], 0.5, "test", 0.0)
        for key in ["overall", "retrieval", "persona", "response_quality", "label"]:
            assert key in result

    def test_label_values(self):
        # Test all label thresholds
        high = self.scorer.compute([{"score": 0.95}], 0.95, "Detailed answer " * 20, 0.0)
        assert high["label"] in ["High", "Medium", "Low"]
        low = self.scorer.compute([], 0.1, "I don't know.", 0.0)
        assert low["label"] == "Low"


# ─────────────────────────────────────────────
#  Conversation Memory Tests
# ─────────────────────────────────────────────

class TestConversationMemory:
    """Test multi-turn memory"""

    def setup_method(self):
        # Memory doesn't need LLM client for basic operations
        self.memory = ConversationMemory.__new__(ConversationMemory)
        self.memory.client = None
        self.memory.history = []
        self.memory.key_facts = []
        self.memory.unresolved_issues = []
        import hashlib, time
        self.memory.session_id = hashlib.md5(str(time.time()).encode()).hexdigest()[:12]
        import datetime as dt
        self.memory.started_at = dt.datetime.now().isoformat()

    def test_add_turns(self):
        self.memory.add_turn("user", "Hello")
        self.memory.add_turn("assistant", "Hi there!")
        assert len(self.memory.history) == 2
        assert self.memory.history[0]["role"] == "user"
        assert self.memory.history[1]["role"] == "assistant"

    def test_extract_error_codes(self):
        self.memory.extract_key_facts("I'm getting error code 401 on the API")
        assert any("401" in fact for fact in self.memory.key_facts)

    def test_extract_features(self):
        self.memory.extract_key_facts("The sync and backup features are broken")
        assert any("sync" in fact.lower() or "backup" in fact.lower() for fact in self.memory.key_facts)

    def test_key_facts_max_10(self):
        for i in range(15):
            self.memory.extract_key_facts(f"error code {i + 100}")
        assert len(self.memory.key_facts) <= 10

    def test_context_summary_empty(self):
        summary = self.memory.get_context_summary()
        assert summary == ""

    def test_context_summary_with_facts(self):
        self.memory.key_facts = ["Error code: 500"]
        summary = self.memory.get_context_summary()
        assert "500" in summary

    def test_reset_clears_history(self):
        self.memory.add_turn("user", "test")
        self.memory.key_facts = ["some fact"]
        self.memory.reset()
        assert len(self.memory.history) == 0
        assert len(self.memory.key_facts) == 0

    def test_session_id_changes_on_reset(self):
        original_id = self.memory.session_id
        self.memory.reset()
        assert self.memory.session_id != original_id


# ─────────────────────────────────────────────
#  Document Loading Tests
# ─────────────────────────────────────────────

class TestDocumentLoading:
    """Test knowledge base loading"""

    def test_load_documents_succeeds(self):
        chunks = load_all_documents()
        assert isinstance(chunks, list)
        assert len(chunks) > 0

    def test_loaded_documents_have_required_fields(self):
        chunks = load_all_documents()
        for chunk in chunks[:5]:
            assert "text" in chunk
            assert "source" in chunk
            assert "section" in chunk
            assert len(chunk["text"]) > 0
            assert len(chunk["source"]) > 0

    def test_includes_pdf_chunks(self):
        chunks = load_all_documents()
        pdf_chunks = [c for c in chunks if c["source"].endswith(".pdf")]
        assert len(pdf_chunks) > 0, "Should have at least one PDF chunk"

    def test_includes_markdown_chunks(self):
        chunks = load_all_documents()
        md_chunks = [c for c in chunks if c["source"].endswith(".md")]
        assert len(md_chunks) > 0, "Should have markdown chunks"

    def test_chunk_text_not_empty(self):
        chunks = load_all_documents()
        for chunk in chunks:
            assert len(chunk["text"].strip()) > 0

    def test_chunk_has_page_number(self):
        chunks = load_all_documents()
        for chunk in chunks[:10]:
            assert "page" in chunk
            assert isinstance(chunk["page"], int)


# ─────────────────────────────────────────────
#  Agent Integration Tests (with API key)
# ─────────────────────────────────────────────

class TestAgentInitialization:
    """Test agent initialization"""

    def test_agent_initializes_with_api_key(self):
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            pytest.skip("No Anthropic API key in environment")
        agent = SupportAgent(api_key=api_key)
        assert agent.persona_detector is not None
        assert agent.vector_store is not None
        assert agent.sentiment_analyzer is not None
        assert agent.confidence_scorer is not None
        assert agent.memory is not None
        assert agent.analytics is not None

    def test_agent_has_session_state(self):
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            pytest.skip("No Anthropic API key in environment")
        agent = SupportAgent(api_key=api_key)
        assert hasattr(agent, "current_persona")
        assert hasattr(agent, "turn_count")
        assert hasattr(agent, "is_escalated")
        assert agent.turn_count == 0
        assert not agent.is_escalated

    def test_agent_chat_returns_expected_keys(self):
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            pytest.skip("No Anthropic API key in environment")
        agent = SupportAgent(api_key=api_key)
        result = agent.chat("How do I reset my password?")
        expected_keys = ["response", "persona", "persona_label", "persona_confidence",
                         "sentiment", "retrieved_docs", "escalated", "confidence_scores"]
        for key in expected_keys:
            assert key in result, f"Missing key: {key}"

    def test_agent_reset_session(self):
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            pytest.skip("No Anthropic API key in environment")
        agent = SupportAgent(api_key=api_key)
        agent.chat("Hello")
        assert agent.turn_count == 1
        agent.reset_session()
        assert agent.turn_count == 0
        assert not agent.is_escalated

    def test_agent_submit_feedback(self):
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            pytest.skip("No Anthropic API key in environment")
        agent = SupportAgent(api_key=api_key)
        result = agent.chat("How do I sync my files?")
        turn_id = result.get("id", "test_id")
        ok = agent.submit_feedback(turn_id, rating=5, helpful=True, comment="Great help!")
        assert ok is True

    def test_agent_analytics(self):
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            pytest.skip("No Anthropic API key in environment")
        agent = SupportAgent(api_key=api_key)
        analytics = agent.get_analytics()
        assert isinstance(analytics, dict)


# ─────────────────────────────────────────────
#  Robustness Tests
# ─────────────────────────────────────────────

class TestRobustness:
    """Test error handling and robustness"""

    def test_persona_detect_handles_long_input(self):
        long_query = "api error " * 500
        persona, confidence, _ = detect_persona(long_query)
        assert persona is not None

    def test_escalation_handles_empty_docs(self):
        result, reason = should_escalate("test", [], 0, 0, 1)
        assert isinstance(result, bool)
        assert isinstance(reason, str)

    def test_sentiment_handles_special_characters(self):
        analyzer = SentimentAnalyzer()
        for text in ["!!!???###", "<script>alert('xss')</script>", "\n\t\r", "👍👎"]:
            try:
                sentiment, score = analyzer.analyze(text)
                assert sentiment in ["positive", "negative", "neutral"]
            except Exception as e:
                pytest.fail(f"Should handle special chars gracefully: {e}")

    def test_confidence_scorer_handles_empty(self):
        scorer = ConfidenceScorer()
        result = scorer.compute([], 0.0, "", 0.0)
        assert 0.0 <= result["overall"] <= 1.0

    def test_document_loading_does_not_crash(self):
        try:
            chunks = load_all_documents()
            assert True
        except Exception as e:
            pytest.fail(f"Document loading should be robust: {e}")

    def test_persona_detect_various_inputs(self):
        test_cases = [
            "Can you check the API logs?",
            "I'm so frustrated with this!!!",
            "What is the business impact?",
            "hello",
            "",
            "1234567890",
        ]
        for query in test_cases:
            try:
                persona, conf, reason = detect_persona(query)
                assert persona in ["technical_expert", "frustrated_user", "business_exec"]
                assert 0.0 <= conf <= 1.0
            except Exception as e:
                pytest.fail(f"Failed for query '{query}': {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
