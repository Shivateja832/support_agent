"""
CloudSync AI Support Agent — Core Agent
Full-featured: RAG + Persona Detection + Sentiment Analysis +
Multi-turn Memory + Confidence Scoring + Escalation + Feedback Collection
"""

import os
import re
import json
import time
import logging
import hashlib
import sqlite3
from pathlib import Path
from typing import Optional
from datetime import datetime

import chromadb
from anthropic import Anthropic

# ─────────────────────────────────────────────
#  Logging
# ─────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("support_agent.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
#  Configuration
# ─────────────────────────────────────────────
DATA_DIR            = Path(__file__).parent.parent / "data"
CHROMA_DIR          = Path(__file__).parent.parent / ".chroma_db"
DB_PATH             = Path(__file__).parent.parent / "analytics.db"
COLLECTION_NAME     = "cloudsync_kb"
TOP_K               = 5
SIMILARITY_THRESHOLD  = 0.35
ESCALATION_THRESHOLD  = 0.28

ESCALATION_KEYWORDS = [
    "lawsuit", "legal action", "attorney", "lawyer", "sue", "court",
    "fraud", "chargeback", "dispute", "regulatory", "gdpr request",
    "data breach", "account hacked", "stolen", "refund", "cancel account",
]

PERSONA_LABELS = {
    "technical_expert": "🔧 Technical Expert",
    "frustrated_user":  "😤 Frustrated User",
    "business_exec":    "💼 Business Executive",
}


# ─────────────────────────────────────────────
#  Analytics Database
# ─────────────────────────────────────────────

class AnalyticsDB:
    """SQLite-backed analytics store."""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    session_id TEXT,
                    timestamp TEXT,
                    user_message TEXT,
                    agent_response TEXT,
                    persona TEXT,
                    persona_confidence REAL,
                    sentiment TEXT,
                    sentiment_score REAL,
                    retrieval_score REAL,
                    escalated INTEGER,
                    turn_count INTEGER
                );
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT,
                    session_id TEXT,
                    timestamp TEXT,
                    rating INTEGER,
                    helpful INTEGER,
                    comment TEXT
                );
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    started_at TEXT,
                    ended_at TEXT,
                    total_turns INTEGER,
                    escalated INTEGER,
                    final_persona TEXT,
                    resolved INTEGER
                );
            """)
            conn.commit()
            conn.close()
            logger.info("Analytics DB initialised")
        except Exception as e:
            logger.error(f"DB init error: {e}")

    def log_conversation(self, data: dict):
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.execute("""
                INSERT OR REPLACE INTO conversations
                (id,session_id,timestamp,user_message,agent_response,
                 persona,persona_confidence,sentiment,sentiment_score,
                 retrieval_score,escalated,turn_count)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                data.get("id", hashlib.md5(str(time.time()).encode()).hexdigest()),
                data.get("session_id", ""),
                data.get("timestamp", datetime.now().isoformat()),
                str(data.get("user_message", ""))[:2000],
                str(data.get("agent_response", ""))[:2000],
                data.get("persona", ""),
                float(data.get("persona_confidence", 0)),
                data.get("sentiment", "neutral"),
                float(data.get("sentiment_score", 0)),
                float(data.get("retrieval_score", 0)),
                int(data.get("escalated", False)),
                int(data.get("turn_count", 0)),
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"DB log_conversation error: {e}")

    def log_feedback(self, session_id: str, conv_id: str, rating: int, helpful: bool, comment: str = ""):
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.execute("""
                INSERT INTO feedback (conversation_id,session_id,timestamp,rating,helpful,comment)
                VALUES (?,?,?,?,?,?)
            """, (conv_id, session_id, datetime.now().isoformat(), int(rating), int(helpful), comment))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"DB log_feedback error: {e}")

    def log_session(self, session_id: str, data: dict):
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.execute("""
                INSERT OR REPLACE INTO sessions
                (id,started_at,ended_at,total_turns,escalated,final_persona,resolved)
                VALUES (?,?,?,?,?,?,?)
            """, (
                session_id,
                data.get("started_at", datetime.now().isoformat()),
                data.get("ended_at", datetime.now().isoformat()),
                int(data.get("total_turns", 0)),
                int(data.get("escalated", False)),
                data.get("final_persona", ""),
                int(data.get("resolved", False)),
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"DB log_session error: {e}")

    def get_analytics_summary(self) -> dict:
        try:
            conn = sqlite3.connect(str(self.db_path))
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM conversations")
            total_convs = c.fetchone()[0]
            c.execute("SELECT COUNT(DISTINCT session_id) FROM conversations")
            total_sessions = c.fetchone()[0]
            c.execute("SELECT persona, COUNT(*) FROM conversations GROUP BY persona ORDER BY COUNT(*) DESC")
            persona_dist = dict(c.fetchall())
            c.execute("SELECT AVG(persona_confidence) FROM conversations WHERE persona_confidence>0")
            avg_conf = c.fetchone()[0] or 0
            c.execute("SELECT AVG(retrieval_score) FROM conversations WHERE retrieval_score>0")
            avg_retrieval = c.fetchone()[0] or 0
            c.execute("SELECT SUM(escalated) FROM conversations")
            escalations = c.fetchone()[0] or 0
            c.execute("SELECT sentiment, COUNT(*) FROM conversations GROUP BY sentiment")
            sentiment_dist = dict(c.fetchall())
            c.execute("SELECT AVG(rating) FROM feedback WHERE rating>0")
            avg_rating = c.fetchone()[0] or 0
            c.execute("SELECT COUNT(*) FROM feedback")
            total_feedback = c.fetchone()[0]
            c.execute("""
                SELECT DATE(timestamp) as day, COUNT(*) as cnt
                FROM conversations GROUP BY day ORDER BY day DESC LIMIT 7
            """)
            daily_volume = [{"date": r[0], "count": r[1]} for r in c.fetchall()]
            conn.close()
            return {
                "total_conversations": total_convs,
                "total_sessions": total_sessions,
                "persona_distribution": persona_dist,
                "avg_persona_confidence": round(avg_conf * 100, 1),
                "avg_retrieval_score": round(avg_retrieval * 100, 1),
                "total_escalations": escalations,
                "escalation_rate": round(escalations / max(total_convs, 1) * 100, 1),
                "sentiment_distribution": sentiment_dist,
                "avg_feedback_rating": round(avg_rating, 2),
                "total_feedback": total_feedback,
                "daily_volume": daily_volume,
            }
        except Exception as e:
            logger.error(f"Analytics error: {e}")
            return {}


# ─────────────────────────────────────────────
#  Document Loaders
# ─────────────────────────────────────────────

def load_markdown(path: Path) -> list:
    text = path.read_text(encoding="utf-8")
    sections = re.split(r"\n(?=#{1,3} )", text)
    chunks = []
    for i, section in enumerate(sections):
        section = section.strip()
        if len(section) < 50:
            continue
        m = re.match(r"^#{1,3} (.+)", section)
        heading = m.group(1) if m else f"Section {i+1}"
        chunks.append({"text": section, "source": path.name, "section": heading, "page": i + 1})
    return chunks


def load_pdf(path: Path) -> list:
    try:
        from pypdf import PdfReader
        reader = PdfReader(str(path))
        chunks = []
        for page_num, page in enumerate(reader.pages, 1):
            text = page.extract_text() or ""
            words = text.split()
            window, overlap = 120, 20
            for start in range(0, max(1, len(words) - overlap), window - overlap):
                chunk_text = " ".join(words[start : start + window]).strip()
                if len(chunk_text) < 80:
                    continue
                chunks.append({"text": chunk_text, "source": path.name,
                                "section": f"Page {page_num}", "page": page_num})
        return chunks
    except Exception as e:
        logger.error(f"PDF load error {path.name}: {e}")
        return []


def load_all_documents() -> list:
    all_chunks = []
    if not DATA_DIR.exists():
        logger.warning(f"Data directory not found: {DATA_DIR}")
        return all_chunks
    for path in DATA_DIR.iterdir():
        if path.suffix == ".md":
            all_chunks.extend(load_markdown(path))
        elif path.suffix == ".pdf":
            all_chunks.extend(load_pdf(path))
    logger.info(f"Loaded {len(all_chunks)} chunks from {DATA_DIR}")
    print(f"[RAG] Loaded {len(all_chunks)} chunks from {DATA_DIR}")
    return all_chunks


# ─────────────────────────────────────────────
#  Embedder  (sentence-transformers with TF-IDF fallback)
# ─────────────────────────────────────────────

class TFIDFEmbedder:
    """
    Fallback embedder using scikit-learn TF-IDF (no internet required).
    Produces 384-dim vectors.  Used automatically when sentence-transformers
    model cannot be downloaded.
    """
    DIM = 384

    def __init__(self):
        from sklearn.feature_extraction.text import TfidfVectorizer
        import numpy as np
        self._vectorizer = TfidfVectorizer(max_features=self.DIM, sublinear_tf=True, ngram_range=(1, 2))
        self._fitted = False
        self._cache: dict = {}
        self._np = np
        logger.info("TFIDFEmbedder initialised (fallback mode)")

    def _fit_if_needed(self, texts: list):
        if not self._fitted:
            self._vectorizer.fit(texts)
            self._fitted = True

    @property
    def using_fallback(self) -> bool:
        return True

    def embed(self, texts: list) -> list:
        np = self._np
        self._fit_if_needed(texts)
        results = []
        for text in texts:
            key = hashlib.md5(text.encode()).hexdigest()
            if key not in self._cache:
                mat = self._vectorizer.transform([text]).toarray()[0]
                # Pad / truncate to DIM
                vec = np.zeros(self.DIM)
                length = min(len(mat), self.DIM)
                vec[:length] = mat[:length]
                norm = float(np.linalg.norm(vec)) or 1.0
                self._cache[key] = (vec / norm).tolist()
            results.append(self._cache[key])
        return results


class SentenceTransformerEmbedder:
    """
    Primary embedder: all-MiniLM-L6-v2 (384-dim semantic vectors).
    Falls back to TFIDFEmbedder if the model cannot be loaded.
    """

    def __init__(self):
        self._cache: dict = {}
        self._model = None
        self._fallback: Optional[TFIDFEmbedder] = None
        self._load_model()

    def _load_model(self):
        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info("SentenceTransformer embedder loaded (all-MiniLM-L6-v2)")
        except Exception as e:
            logger.warning(f"SentenceTransformer unavailable ({e}). Using TF-IDF fallback.")
            self._fallback = TFIDFEmbedder()

    def embed(self, texts: list) -> list:
        if self._fallback:
            return self._fallback.embed(texts)
        results = []
        for text in texts:
            key = hashlib.md5(text.encode()).hexdigest()
            if key not in self._cache:
                vec = self._model.encode(text, convert_to_numpy=False)
                self._cache[key] = vec.tolist() if hasattr(vec, "tolist") else list(vec)
            results.append(self._cache[key])
        return results

    @property
    def using_fallback(self) -> bool:
        return self._fallback is not None


# ─────────────────────────────────────────────
#  Vector Store
# ─────────────────────────────────────────────

class VectorStore:
    def __init__(self):
        self.chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        self.embedder = SentenceTransformerEmbedder()
        self.collection = None
        logger.info("VectorStore initialised")

    def _hash(self, text: str, idx: int) -> str:
        return hashlib.md5(f"{idx}:{text[:50]}".encode()).hexdigest()[:16]

    def build_index(self, chunks: list, force_rebuild: bool = False):
        try:
            existing = [c.name for c in self.chroma_client.list_collections()]
            if COLLECTION_NAME in existing and not force_rebuild:
                self.collection = self.chroma_client.get_collection(COLLECTION_NAME)
                logger.info(f"Using existing index ({self.collection.count()} vectors)")
                print(f"[RAG] Using existing index with {self.collection.count()} vectors")
                return
            if COLLECTION_NAME in existing:
                self.chroma_client.delete_collection(COLLECTION_NAME)
            self.collection = self.chroma_client.create_collection(
                COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
            )
            # For TF-IDF embedder: fit on ALL texts first
            if self.embedder.using_fallback:
                all_texts = [c["text"] for c in chunks]
                self.embedder.embed(all_texts[:200])  # prime the vectorizer

            batch_size = 100
            for i in range(0, len(chunks), batch_size):
                batch = chunks[i : i + batch_size]
                texts = [c["text"] for c in batch]
                embeddings = self.embedder.embed(texts)
                ids = [self._hash(c["text"], i + j) for j, c in enumerate(batch)]
                metadatas = [{"source": c["source"], "section": c["section"], "page": c["page"]}
                             for c in batch]
                self.collection.add(ids=ids, embeddings=embeddings,
                                    documents=texts, metadatas=metadatas)
            logger.info(f"Index built: {len(chunks)} chunks")
            print(f"[RAG] Index built with {len(chunks)} chunks")
        except Exception as e:
            logger.error(f"Index build error: {e}")
            raise

    def retrieve(self, query: str, top_k: int = TOP_K) -> list:
        if not self.collection:
            return []
        try:
            q_emb = self.embedder.embed([query])
            results = self.collection.query(
                query_embeddings=q_emb, n_results=top_k,
                include=["documents", "metadatas", "distances"]
            )
            hits = []
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0],
            ):
                hits.append({
                    "text": doc,
                    "source": meta["source"],
                    "section": meta["section"],
                    "page": meta["page"],
                    "score": round(1 - dist, 4),
                })
            return hits
        except Exception as e:
            logger.error(f"Retrieval error: {e}")
            return []


# ─────────────────────────────────────────────
#  Sentiment Analyser
# ─────────────────────────────────────────────

class SentimentAnalyzer:
    """Rule-based sentiment analysis with score from -1.0 to +1.0."""

    POSITIVE_WORDS = [
        "thanks", "thank you", "great", "excellent", "perfect", "awesome", "love",
        "helpful", "resolved", "fixed", "works", "working", "appreciate", "wonderful",
        "fantastic", "brilliant", "good", "nice", "happy", "pleased", "satisfied",
    ]
    NEGATIVE_WORDS = [
        "terrible", "awful", "horrible", "bad", "broken", "useless", "garbage",
        "hate", "angry", "furious", "frustrated", "ridiculous", "unacceptable",
        "worst", "fail", "failed", "failing", "wrong", "stupid", "disgusting",
        "never works", "still broken", "not working", "wasted", "waste",
    ]

    def analyze(self, text: str) -> tuple:
        """Returns (sentiment, score).  sentiment in {positive,negative,neutral}."""
        text_lower = text.lower()
        pos = sum(1 for w in self.POSITIVE_WORDS if w in text_lower)
        neg = sum(1 for w in self.NEGATIVE_WORDS if w in text_lower)

        excl_count = text.count("!")
        # Count all-caps words only (not just a sentence-starting capital)
        words_in_text = text.split()
        caps_count = sum(1 for w in words_in_text if len(w) > 1 and w.isupper())
        caps_ratio = caps_count / max(len(words_in_text), 1)
        neg_boost = min(excl_count * 0.3 + caps_ratio * 2, 2.0)
        neg += neg_boost

        total = pos + neg
        if total == 0:
            return "neutral", 0.0

        score = max(-1.0, min(1.0, (pos - neg) / total))
        if score > 0.15:
            sentiment = "positive"
        elif score < -0.15:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        return sentiment, round(score, 3)

    def get_label(self, sentiment: str) -> str:
        return {"positive": "😊 Positive", "negative": "😤 Negative", "neutral": "😐 Neutral"}.get(
            sentiment, "😐 Neutral"
        )


# ─────────────────────────────────────────────
#  Persona Detector
# ─────────────────────────────────────────────

class PersonaDetector:
    """Triple-layer: rule-based → ML → LLM."""

    TECHNICAL_PATTERNS = [
        r"\bapi\b", r"\berror\s*code\b", r"\bstack\s*trace\b", r"\bhttp\s*[45]\d\d\b",
        r"\bwebhook\b", r"\boauth\b", r"\bjwt\b", r"\bdebugg?\b", r"\blatency\b",
        r"\bendpoint\b", r"\bpayload\b", r"\bauth(?:entication|orization)?\b",
        r"\blogs?\b", r"\bconfigur\b", r"\bssl\b", r"\bcurl\b", r"\bsdks?\b",
        r"\bparse\b", r"\bexception\b", r"\bquery\b", r"\bdns\b", r"\btls\b",
    ]
    FRUSTRATED_PATTERNS = [
        r"(?:not\s+working|doesn.t\s+work|broken|terrible|awful|horrible)",
        r"(?:wasted?|hours?|days?|forever|again|still|keep)",
        r"\b(?:angry|furious|frustrated)\b",
        r"(?:terrible|worst|hate|useless|garbage|ridiculous)",
        r"(?:fix\s+this|sort\s+this|come\s+on|seriously|unacceptable)",
        r"(?:!!!|!!\?|\?\?\?)", r"\bwhy\s+(?:is|does|won.t|can.t)\b",
        r"\b(?:sick|tired|fed\s+up)\s+of\b",
    ]
    EXEC_PATTERNS = [
        r"\b(?:business|revenue|roi|impact|cost)\b", r"\b(?:downtime|outage|sla)\b",
        r"\b(?:resolve|timeline|eta|when\s+will)\b", r"\b(?:team|staff|employees?)\b",
        r"\b(?:operations?|productivity|efficiency)\b",
        r"\b(?:executive|ceo|cto|vp|director)\b",
        r"\b(?:contract|vendor|procurement)\b",
        r"\b(?:summary|brief|overview|concise)\b",
        r"\b(?:affected|impact(?:ing|ed)?)\b",
    ]

    def __init__(self, client: Anthropic):
        self.client = client
        self._cache: dict = {}

    def _score(self, text: str, patterns: list) -> int:
        tl = text.lower()
        return sum(1 for p in patterns if re.search(p, tl))

    def detect(self, message: str, history: list = None) -> tuple:
        """Returns (persona_key, confidence 0-1, reasoning)."""
        context = message
        if history:
            recent = " ".join(m["content"] for m in history[-4:] if m["role"] == "user")
            context = recent + " " + message

        key = hashlib.md5(context.encode()).hexdigest()
        if key in self._cache:
            return self._cache[key]

        scores = {
            "technical_expert": self._score(context, self.TECHNICAL_PATTERNS),
            "frustrated_user":  self._score(context, self.FRUSTRATED_PATTERNS),
            "business_exec":    self._score(context, self.EXEC_PATTERNS),
        }
        max_score = max(scores.values())

        if max_score >= 3:
            persona = max(scores, key=scores.get)
            confidence = min(0.95, 0.60 + max_score * 0.07)
            result = (persona, confidence, f"Rule-based: {scores}")
            self._cache[key] = result
            return result

        # ML fallback
        try:
            from train_persona_classifier import predict as ml_predict
            persona, confidence = ml_predict(context)
            if confidence > 0.55:
                result = (persona, confidence, f"ML: conf={confidence:.2f}")
                self._cache[key] = result
                return result
        except Exception:
            pass

        # LLM fallback
        try:
            resp = self.client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=120,
                system=(
                    "Classify the user message into exactly one persona. "
                    'Respond with JSON only: {"persona": "...", "confidence": 0.0, "reason": "..."}\n'
                    "Personas:\n"
                    "- technical_expert: technical terms, logs, API, configs\n"
                    "- frustrated_user: emotional, frustrated, urgent complaints\n"
                    "- business_exec: ROI, SLA, timeline, business impact, concise\n"
                    "confidence is 0.0-1.0."
                ),
                messages=[{"role": "user", "content": f"Classify: {context[:600]}"}],
            )
            raw = re.sub(r"^```(?:json)?\s*", "", resp.content[0].text.strip())
            raw = re.sub(r"\s*```$", "", raw)
            data = json.loads(raw)
            persona = data.get("persona", "frustrated_user")
            if persona not in scores:
                persona = "frustrated_user"
            confidence = float(data.get("confidence", 0.6))
            result = (persona, confidence, f"LLM: {data.get('reason', '')}")
        except Exception as e:
            persona = max(scores, key=scores.get) if max_score > 0 else "frustrated_user"
            confidence = 0.5
            result = (persona, confidence, f"Fallback ({type(e).__name__})")

        self._cache[key] = result
        return result


# ─────────────────────────────────────────────
#  Escalation Logic
# ─────────────────────────────────────────────

class EscalationChecker:
    def __init__(self, max_turns: int = 6, low_score_limit: int = 3):
        self.max_turns = max_turns
        self.low_score_limit = low_score_limit

    def should_escalate(
        self, message: str, retrieval_hits: list, turn_count: int,
        low_confidence_count: int, persona: str, dissatisfied_count: int,
    ) -> tuple:
        msg_lower = message.lower()
        for kw in ESCALATION_KEYWORDS:
            if kw in msg_lower:
                return True, f"Sensitive topic detected: '{kw}'"
        if not retrieval_hits:
            return True, "No relevant knowledge base articles found"
        if retrieval_hits:
            best = max(h["score"] for h in retrieval_hits)
            if best < ESCALATION_THRESHOLD:
                return True, f"Low retrieval confidence (best: {best:.2f})"
        if low_confidence_count >= self.low_score_limit:
            return True, f"Repeated low-confidence responses ({low_confidence_count}x)"
        if dissatisfied_count >= 2:
            return True, f"User dissatisfied {dissatisfied_count} times"
        if turn_count >= self.max_turns:
            return True, f"Conversation limit reached ({turn_count} turns)"
        return False, ""


# ─────────────────────────────────────────────
#  Response Generator
# ─────────────────────────────────────────────

PERSONA_SYSTEM_PROMPTS = {
    "technical_expert": """You are a highly skilled CloudSync technical support engineer.
The user is a Technical Expert:
- Use precise technical terminology; skip basics
- Include root cause analysis and step-by-step diagnostics
- Reference error codes, API endpoints, logs, configuration fields
- Be thorough — this user values depth
Answer ONLY from the provided knowledge base excerpts. If the answer is not there, say so clearly.""",

    "frustrated_user": """You are an empathetic CloudSync customer support specialist.
The user is Frustrated — upset and needs immediate help:
- Start with ONE sincere sentence acknowledging their frustration
- Use simple, jargon-free language
- Give numbered action steps they can take RIGHT NOW
- Be warm, patient, and reassuring
- End with a clear next step or escalation offer
Answer ONLY from the provided knowledge base excerpts.""",

    "business_exec": """You are a CloudSync enterprise customer success representative.
The user is a Business Executive:
- Lead with business impact and resolution timeline
- Be concise — use bullet points
- No technical jargon; speak in business terms
- Quantify impact where possible
- End with executive summary and next steps (under 200 words)
Answer ONLY from the provided knowledge base excerpts.""",
}


class ResponseGenerator:
    def __init__(self, client: Anthropic):
        self.client = client

    def generate(
        self, message: str, persona: str, retrieval_hits: list,
        conversation_history: list, sentiment: str = "neutral",
    ) -> str:
        system = PERSONA_SYSTEM_PROMPTS.get(persona, PERSONA_SYSTEM_PROMPTS["frustrated_user"])
        if sentiment == "negative" and persona != "frustrated_user":
            system += "\n\nNote: The user seems frustrated. Be extra empathetic."
        elif sentiment == "positive":
            system += "\n\nNote: The user is in a positive mood. Match their energy warmly."

        if retrieval_hits:
            parts = [f"[Source {i}: {h['source']} | {h['section']}]\n{h['text']}"
                     for i, h in enumerate(retrieval_hits, 1)]
            kb = "\n\n---\n\n".join(parts)
            system += f"\n\n=== KNOWLEDGE BASE EXCERPTS ===\n{kb}\n=== END ===\n\nUse ONLY these excerpts. Cite sources naturally."
        else:
            system += "\n\nNo relevant KB articles found. Acknowledge this and offer escalation."

        messages = [{"role": t["role"], "content": t["content"]}
                    for t in conversation_history[-8:]]
        messages.append({"role": "user", "content": message})

        try:
            resp = self.client.messages.create(
                model="claude-sonnet-4-6", max_tokens=700,
                system=system, messages=messages,
            )
            return resp.content[0].text.strip()
        except Exception as e:
            logger.error(f"Response generation error: {e}")
            return ("I'm sorry, I encountered an error generating a response. "
                    "Please try again or contact support directly.")

    def generate_handoff_summary(
        self, persona: str, issue_summary: str, conversation_history: list,
        retrieved_docs: list, escalation_reason: str,
        sentiment: str = "neutral", sentiment_score: float = 0.0,
    ) -> dict:
        attempted = []
        for t in conversation_history:
            if t["role"] == "assistant":
                steps = re.findall(r"\d+\.\s+(.+?)(?:\n|$)", t["content"])
                attempted.extend(steps[:3])
        attempted = list(dict.fromkeys(attempted))[:5]
        docs_used = list({h["source"] for h in retrieved_docs}) if retrieved_docs else []

        try:
            sr = self.client.messages.create(
                model="claude-sonnet-4-6", max_tokens=200,
                system="Summarise the customer's core issue in 1-2 sentences. Be specific.",
                messages=[{"role": "user",
                           "content": "Conversation:\n" + "\n".join(
                               t["role"] + ": " + t["content"]
                               for t in conversation_history[-6:])}]
            )
            issue_text = sr.content[0].text.strip()
        except Exception:
            issue_text = issue_summary

        rec_map = {
            "legal": "Route to Legal immediately. No commitments.",
            "billing": "Route to Billing. Review account history first.",
            "sensitive": "Senior support required. Verify account first.",
            "confidence": "Tier 2 technical investigation needed.",
            "dissatisfied": "Immediate senior attention + possible service credit.",
            "limit": "Assign dedicated support engineer.",
            "no relevant": "Outside KB scope — product team review.",
        }
        recommendation = "Escalate to Tier 2 support."
        for k, v in rec_map.items():
            if k.lower() in escalation_reason.lower():
                recommendation = v
                break

        return {
            "timestamp": datetime.now().isoformat(),
            "persona": PERSONA_LABELS.get(persona, persona),
            "issue": issue_text,
            "escalation_reason": escalation_reason,
            "documents_used": docs_used,
            "attempted_steps": attempted or ["General troubleshooting attempted"],
            "conversation_turns": len([t for t in conversation_history if t["role"] == "user"]),
            "sentiment": sentiment,
            "sentiment_score": round(sentiment_score, 3),
            "recommendation": recommendation,
            "priority": "HIGH" if any(k in escalation_reason.lower()
                                      for k in ["legal", "breach", "fraud", "critical"]) else "MEDIUM",
        }


# ─────────────────────────────────────────────
#  Confidence Scorer
# ─────────────────────────────────────────────

class ConfidenceScorer:
    def compute(self, retrieval_hits: list, persona_confidence: float,
                response_text: str, sentiment_score: float) -> dict:
        if retrieval_hits:
            best = max(h["score"] for h in retrieval_hits)
            avg  = sum(h["score"] for h in retrieval_hits) / len(retrieval_hits)
            retrieval_conf = best * 0.7 + avg * 0.3
        else:
            retrieval_conf = 0.0

        resp_len = len(response_text.split())
        length_score = min(1.0, resp_len / 100)
        uncertainty = sum(0.15 for p in
                          ["i'm not sure", "i don't know", "unable to find", "no information"]
                          if p in response_text.lower())
        response_quality = max(0.0, length_score - uncertainty)

        overall = round(min(1.0, max(0.0,
            retrieval_conf    * 0.45 +
            persona_confidence * 0.30 +
            response_quality   * 0.25
        )), 3)
        label = "High" if overall >= 0.7 else ("Medium" if overall >= 0.45 else "Low")
        return {"overall": overall, "retrieval": round(retrieval_conf, 3),
                "persona": round(persona_confidence, 3),
                "response_quality": round(response_quality, 3), "label": label}


# ─────────────────────────────────────────────
#  Conversation Memory
# ─────────────────────────────────────────────

class ConversationMemory:
    def __init__(self, client: Anthropic):
        self.client = client
        self.history: list = []
        self.key_facts: list = []
        self.unresolved_issues: list = []
        self.session_id: str = hashlib.md5(str(time.time()).encode()).hexdigest()[:12]
        self.started_at: str = datetime.now().isoformat()

    def add_turn(self, role: str, content: str, meta: dict = None):
        self.history.append({
            "role": role, "content": content,
            "timestamp": datetime.now().isoformat(),
            "meta": meta or {},
        })

    def extract_key_facts(self, user_message: str):
        for code in re.findall(r"\b(?:error|code|http)\s*:?\s*(\d{3,})\b", user_message, re.I):
            f = f"Error code: {code}"
            if f not in self.key_facts:
                self.key_facts.append(f)
        for feat in set(re.findall(
            r"\b(?:sync|backup|restore|webhook|api|dashboard|billing|password|login)\b",
            user_message, re.I
        )):
            f = f"Feature mentioned: {feat.lower()}"
            if f not in self.key_facts:
                self.key_facts.append(f)
        self.key_facts = self.key_facts[-10:]

    def get_context_summary(self) -> str:
        if not self.key_facts:
            return ""
        return "Key facts from this conversation: " + "; ".join(self.key_facts)

    def reset(self):
        self.history = []
        self.key_facts = []
        self.unresolved_issues = []
        self.session_id = hashlib.md5(str(time.time()).encode()).hexdigest()[:12]
        self.started_at = datetime.now().isoformat()


# ─────────────────────────────────────────────
#  Main Support Agent
# ─────────────────────────────────────────────

class SupportAgent:
    """
    CloudSync AI Support Agent — production-ready.
    RAG · Persona Detection · Sentiment Analysis · Multi-turn Memory
    Confidence Scoring · Escalation · Human Handoff · Feedback · Analytics
    """

    def __init__(self, api_key: str, rebuild_index: bool = False):
        logger.info("Initialising SupportAgent…")
        self.client             = Anthropic(api_key=api_key)
        self.vector_store       = VectorStore()
        self.persona_detector   = PersonaDetector(self.client)
        self.escalation_checker = EscalationChecker()
        self.response_generator = ResponseGenerator(self.client)
        self.sentiment_analyzer = SentimentAnalyzer()
        self.confidence_scorer  = ConfidenceScorer()
        self.memory             = ConversationMemory(self.client)
        self.analytics          = AnalyticsDB()

        # Session state
        self.turn_count: int           = 0
        self.low_confidence_count: int = 0
        self.dissatisfied_count: int   = 0
        self.all_retrieved_docs: list  = []
        self.is_escalated: bool        = False
        self.current_persona: str      = "frustrated_user"
        self.persona_confidence: float = 0.0
        self.last_confidence_scores: dict = {}

        chunks = load_all_documents()
        self.vector_store.build_index(chunks, force_rebuild=rebuild_index)
        logger.info("SupportAgent ready")

    # Keep old property for UI compatibility
    @property
    def conversation_history(self) -> list:
        return self.memory.history

    def _detect_dissatisfaction(self, message: str) -> bool:
        patterns = [
            r"(?:still not|doesn['\"]t help|not helpful|that didn['\"]t|useless|wrong answer)",
            r"(?:i already|i said|not what i asked|please read|not working still)",
            r"(?:terrible|awful|horrible|unacceptable|ridiculous)",
        ]
        ml = message.lower()
        return any(re.search(p, ml) for p in patterns)

    def chat(self, user_message: str) -> dict:
        self.turn_count += 1
        turn_id = hashlib.md5(
            f"{self.memory.session_id}:{self.turn_count}".encode()
        ).hexdigest()[:12]
        logger.info(f"[Turn {self.turn_count}] {user_message[:80]}")

        sentiment, sentiment_score = self.sentiment_analyzer.analyze(user_message)
        persona, confidence, persona_reason = self.persona_detector.detect(
            user_message, self.memory.history
        )
        self.current_persona    = persona
        self.persona_confidence = confidence

        self.memory.extract_key_facts(user_message)
        if self._detect_dissatisfaction(user_message):
            self.dissatisfied_count += 1

        hits = self.vector_store.retrieve(user_message, top_k=TOP_K)
        self.all_retrieved_docs.extend(hits)
        if not hits or max(h["score"] for h in hits) < SIMILARITY_THRESHOLD:
            self.low_confidence_count += 1

        should_esc, esc_reason = self.escalation_checker.should_escalate(
            message=user_message, retrieval_hits=hits,
            turn_count=self.turn_count,
            low_confidence_count=self.low_confidence_count,
            persona=persona, dissatisfied_count=self.dissatisfied_count,
        )

        handoff_summary = None
        if should_esc and not self.is_escalated:
            self.is_escalated = True
            handoff_summary = self.response_generator.generate_handoff_summary(
                persona=persona, issue_summary=user_message,
                conversation_history=self.memory.history,
                retrieved_docs=self.all_retrieved_docs,
                escalation_reason=esc_reason,
                sentiment=sentiment, sentiment_score=sentiment_score,
            )

        response_text = self.response_generator.generate(
            message=user_message, persona=persona,
            retrieval_hits=hits, conversation_history=self.memory.history,
            sentiment=sentiment,
        )

        conf_scores = self.confidence_scorer.compute(
            retrieval_hits=hits, persona_confidence=confidence,
            response_text=response_text, sentiment_score=sentiment_score,
        )
        self.last_confidence_scores = conf_scores

        self.memory.add_turn("user", user_message, meta={"sentiment": sentiment})
        self.memory.add_turn("assistant", response_text,
                             meta={"persona": persona, "confidence": conf_scores})

        self.analytics.log_conversation({
            "id": turn_id,
            "session_id": self.memory.session_id,
            "user_message": user_message,
            "agent_response": response_text,
            "persona": persona,
            "persona_confidence": confidence,
            "sentiment": sentiment,
            "sentiment_score": sentiment_score,
            "retrieval_score": max((h["score"] for h in hits), default=0),
            "escalated": self.is_escalated,
            "turn_count": self.turn_count,
        })

        return {
            "id": turn_id,
            "response": response_text,
            "persona": persona,
            "persona_label": PERSONA_LABELS.get(persona, persona),
            "persona_confidence": round(confidence * 100, 1),
            "sentiment": sentiment,
            "sentiment_score": sentiment_score,
            "sentiment_label": self.sentiment_analyzer.get_label(sentiment),
            "retrieved_docs": hits,
            "escalated": self.is_escalated,
            "escalation_reason": esc_reason if self.is_escalated else "",
            "handoff_summary": handoff_summary,
            "confidence_scores": conf_scores,
            "turn_count": self.turn_count,
            "session_id": self.memory.session_id,
            "key_facts": self.memory.key_facts.copy(),
            "metadata": {
                "low_confidence_count": self.low_confidence_count,
                "dissatisfied_count": self.dissatisfied_count,
                "persona_reason": persona_reason,
                "best_retrieval_score": max((h["score"] for h in hits), default=0),
            },
        }

    def submit_feedback(self, turn_id: str, rating: int, helpful: bool, comment: str = "") -> bool:
        try:
            self.analytics.log_feedback(
                session_id=self.memory.session_id,
                conv_id=turn_id, rating=rating,
                helpful=helpful, comment=comment,
            )
            return True
        except Exception as e:
            logger.error(f"Feedback error: {e}")
            return False

    def get_analytics(self) -> dict:
        return self.analytics.get_analytics_summary()

    def reset_session(self):
        self.analytics.log_session(self.memory.session_id, {
            "started_at": self.memory.started_at,
            "ended_at": datetime.now().isoformat(),
            "total_turns": self.turn_count,
            "escalated": self.is_escalated,
            "final_persona": self.current_persona,
            "resolved": not self.is_escalated,
        })
        self.memory.reset()
        self.turn_count            = 0
        self.low_confidence_count  = 0
        self.dissatisfied_count    = 0
        self.all_retrieved_docs    = []
        self.is_escalated          = False
        self.current_persona       = "frustrated_user"
        self.persona_confidence    = 0.0
        self.last_confidence_scores = {}


# ─────────────────────────────────────────────
#  Module-level helpers (used by unit tests)
# ─────────────────────────────────────────────

def detect_persona(message: str, history: list = None) -> tuple:
    """Standalone rule-based persona detection (no LLM / API key needed)."""
    text = (message or "").lower()
    patterns = {
        "technical_expert": PersonaDetector.TECHNICAL_PATTERNS,
        "frustrated_user":  PersonaDetector.FRUSTRATED_PATTERNS,
        "business_exec":    PersonaDetector.EXEC_PATTERNS,
    }
    scores = {p: sum(1 for rx in rxs if re.search(rx, text))
              for p, rxs in patterns.items()}
    max_score = max(scores.values())
    if max_score > 0:
        best = max(scores, key=scores.get)
        confidence = min(0.95, 0.60 + max_score * 0.07)
    else:
        best, confidence = "frustrated_user", 0.5
    return best, confidence, f"Rule-based: {scores}"


def should_escalate(
    query: str, retrieved_docs: list,
    low_conf_count: int, dissatisfaction_count: int, turn_count: int,
    max_turns: int = 6, low_score_limit: int = 3,
) -> tuple:
    """Standalone escalation check (no API key needed)."""
    checker = EscalationChecker(max_turns=max_turns, low_score_limit=low_score_limit)
    return checker.should_escalate(
        message=query, retrieval_hits=retrieved_docs,
        turn_count=turn_count, low_confidence_count=low_conf_count,
        persona="frustrated_user", dissatisfied_count=dissatisfaction_count,
    )
