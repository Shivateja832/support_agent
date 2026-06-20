"""
CloudSync AI Support Agent — Streamlit UI
Full-featured: Persona-Adaptive RAG + Sentiment Analysis + Confidence Scoring +
Multi-turn Memory + Human Escalation + Feedback Collection + Analytics Dashboard
"""

import os
import json
import time
from dotenv import load_dotenv
import streamlit as st
from datetime import datetime
from pathlib import Path

load_dotenv()

st.set_page_config(
    page_title="CloudSync AI Support",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #0f1117; }
.header-banner {
    background: linear-gradient(135deg, #1a2744 0%, #0d1b35 50%, #1a2744 100%);
    border-bottom: 1px solid rgba(99,179,237,0.2);
    padding: 18px 28px; margin: -1rem -1rem 1.5rem -1rem;
    display: flex; align-items: center; gap: 16px;
    border-radius: 0 0 12px 12px;
}
.header-title { font-size: 22px; font-weight: 700; color: #e2e8f0; margin: 0; }
.header-subtitle { font-size: 12px; color: #63b3ed; margin: 2px 0 0 0; letter-spacing: 0.5px; font-weight: 500; text-transform: uppercase; }
.header-status { margin-left: auto; display: flex; align-items: center; gap: 8px; font-size: 12px; color: #68d391; font-weight: 600; }
.status-dot { width: 8px; height: 8px; background: #68d391; border-radius: 50%; animation: pulse 2s infinite; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }
.chat-container { display: flex; flex-direction: column; gap: 16px; padding: 8px 0; }
.msg-user { display: flex; justify-content: flex-end; gap: 10px; align-items: flex-start; }
.msg-agent { display: flex; justify-content: flex-start; gap: 10px; align-items: flex-start; }
.bubble-user {
    background: linear-gradient(135deg, #2b4a8a 0%, #1e3a6a 100%);
    color: #e2e8f0; border-radius: 18px 4px 18px 18px;
    padding: 12px 18px; max-width: 72%; font-size: 14px; line-height: 1.6;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3); border: 1px solid rgba(99,179,237,0.15);
}
.bubble-agent {
    background: linear-gradient(135deg, #1a2233 0%, #1e2840 100%);
    color: #cbd5e0; border-radius: 4px 18px 18px 18px;
    padding: 14px 18px; max-width: 78%; font-size: 14px; line-height: 1.7;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.08);
}
.avatar-user {
    width: 36px; height: 36px; background: linear-gradient(135deg, #4a90d9, #2b6cb0);
    border-radius: 50%; display: flex; align-items: center; justify-content: center;
    font-size: 16px; flex-shrink: 0; box-shadow: 0 2px 6px rgba(0,0,0,0.3);
}
.avatar-agent {
    width: 36px; height: 36px; background: linear-gradient(135deg, #2d3748, #1a202c);
    border-radius: 50%; display: flex; align-items: center; justify-content: center;
    font-size: 16px; flex-shrink: 0; border: 1px solid rgba(99,179,237,0.3);
}
.msg-time { font-size: 10px; color: #4a5568; margin-top: 4px; text-align: right; }
.persona-badge {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600;
    margin-bottom: 6px; letter-spacing: 0.3px;
}
.persona-technical_expert { background: rgba(66,153,225,0.15); color: #63b3ed; border: 1px solid rgba(66,153,225,0.3); }
.persona-frustrated_user { background: rgba(245,101,101,0.15); color: #fc8181; border: 1px solid rgba(245,101,101,0.3); }
.persona-business_exec { background: rgba(154,230,180,0.15); color: #68d391; border: 1px solid rgba(154,230,180,0.3); }
.sentiment-badge {
    display: inline-flex; align-items: center; gap: 4px;
    padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 500; margin-left: 6px;
}
.sentiment-positive { background: rgba(104,211,145,0.15); color: #68d391; }
.sentiment-negative { background: rgba(252,129,129,0.15); color: #fc8181; }
.sentiment-neutral { background: rgba(160,174,192,0.15); color: #a0aec0; }
.source-card {
    background: rgba(26,32,46,0.8); border: 1px solid rgba(255,255,255,0.07);
    border-radius: 8px; padding: 10px 14px; margin: 6px 0; font-size: 12px; color: #a0aec0;
}
.source-card-header { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }
.source-name { font-weight: 600; color: #63b3ed; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; }
.source-score { margin-left: auto; font-size: 11px; font-weight: 600; }
.source-section { color: #718096; font-size: 12px; }
.escalation-banner {
    background: linear-gradient(135deg, rgba(245,101,101,0.1), rgba(229,62,62,0.15));
    border: 1px solid rgba(245,101,101,0.4); border-radius: 12px; padding: 16px 20px; margin: 12px 0;
}
.escalation-title { color: #fc8181; font-weight: 700; font-size: 15px; margin-bottom: 6px; }
.escalation-reason { color: #feb2b2; font-size: 13px; }
.handoff-card {
    background: linear-gradient(135deg, #1a2233, #1e2840);
    border: 1px solid rgba(99,179,237,0.2); border-radius: 12px; padding: 20px;
    margin: 12px 0; font-family: 'JetBrains Mono', monospace; font-size: 12px;
    color: #a0aec0; white-space: pre-wrap; line-height: 1.8;
}
.conf-bar-bg { background: rgba(255,255,255,0.08); border-radius: 4px; height: 4px; width: 100%; margin-top: 4px; }
.conf-bar-fill { height: 4px; border-radius: 4px; transition: width 0.5s ease; }
.sidebar-section {
    background: rgba(26,32,46,0.6); border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px; padding: 14px; margin-bottom: 12px;
}
.sidebar-section-title {
    font-size: 11px; font-weight: 700; color: #63b3ed;
    text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px;
}
.stat-row {
    display: flex; justify-content: space-between; align-items: center;
    padding: 5px 0; border-bottom: 1px solid rgba(255,255,255,0.04);
}
.stat-label { font-size: 12px; color: #718096; }
.stat-value { font-size: 12px; font-weight: 600; color: #e2e8f0; }
.feedback-stars { display: flex; gap: 4px; }
.welcome-card {
    background: linear-gradient(135deg, #1a2233 0%, #1e2840 100%);
    border: 1px solid rgba(99,179,237,0.15); border-radius: 16px;
    padding: 40px; text-align: center; margin: 20px 0;
}
.welcome-icon { font-size: 52px; margin-bottom: 16px; }
.welcome-title { font-size: 24px; font-weight: 700; color: #e2e8f0; margin-bottom: 8px; }
.welcome-sub { font-size: 14px; color: #718096; line-height: 1.7; max-width: 500px; margin: 0 auto; }
.stTextArea textarea {
    background: #1a2233 !important; color: #e2e8f0 !important;
    border: 1px solid rgba(99,179,237,0.25) !important; border-radius: 12px !important;
    font-family: 'Inter', sans-serif !important; font-size: 14px !important;
    padding: 14px !important; resize: none !important;
}
.stButton > button {
    background: linear-gradient(135deg, #2b4a8a 0%, #1e3a6a 100%) !important;
    color: #e2e8f0 !important; border: 1px solid rgba(99,179,237,0.3) !important;
    border-radius: 10px !important; font-weight: 600 !important; font-size: 14px !important;
    padding: 10px 24px !important; transition: all 0.2s !important; width: 100% !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #3a5fa0 0%, #2b4a8a 100%) !important;
    transform: translateY(-1px) !important;
}
.stSidebar { background: #0d1117 !important; border-right: 1px solid rgba(255,255,255,0.06) !important; }
.block-container { padding-top: 0 !important; max-width: 1200px; }
footer { display: none !important; }
#MainMenu { display: none !important; }
header[data-testid="stHeader"] { background: transparent !important; }
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-thumb { background: rgba(99,179,237,0.2); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

import sys
sys.path.insert(0, str(Path(__file__).parent))
from src.agent import SupportAgent, PERSONA_LABELS

# ─── Session State ───
def init_session():
    defaults = {
        "agent": None, "messages": [], "api_key": "",
        "initialized": False, "chat_input": "",
        "example_query": None, "auto_send": False,
        "active_tab": "chat", "pending_feedback": {},
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()

PERSONA_ICONS = {"technical_expert": "🔧", "frustrated_user": "😤", "business_exec": "💼"}
PERSONA_COLORS = {"technical_expert": "#63b3ed", "frustrated_user": "#fc8181", "business_exec": "#68d391"}

def score_color(s): return "#68d391" if s >= 0.7 else ("#f6ad55" if s >= 0.45 else "#fc8181")
def fmt_ts(ts):
    try: return datetime.fromisoformat(ts).strftime("%I:%M %p")
    except: return ""

def get_agent():
    if st.session_state.agent is None:
        api_key = st.session_state.api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key: return None
        with st.spinner("🔧 Initializing AI Support Agent and loading knowledge base..."):
            try:
                agent = SupportAgent(api_key=api_key)
                st.session_state.agent = agent
                st.session_state.initialized = True
            except Exception as e:
                st.error(f"Failed to initialize agent: {e}")
                return None
    return st.session_state.agent


# ─── Sidebar ───
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:16px 0 20px;">
        <div style="font-size:36px;">🤖</div>
        <div style="font-size:16px;font-weight:700;color:#e2e8f0;margin-top:8px;">CloudSync</div>
        <div style="font-size:11px;color:#63b3ed;letter-spacing:1px;text-transform:uppercase;">AI Support Agent</div>
    </div>
    """, unsafe_allow_html=True)

    # Navigation
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-section-title">📍 Navigation</div>', unsafe_allow_html=True)
    if st.button("💬 Chat", key="nav_chat"): st.session_state.active_tab = "chat"; st.rerun()
    if st.button("📊 Analytics Dashboard", key="nav_analytics"): st.session_state.active_tab = "analytics"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # API Key
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-section-title">🔑 Configuration</div>', unsafe_allow_html=True)
    env_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if env_key:
        st.success("✅ API key loaded from environment")
        st.session_state.api_key = env_key
    else:
        key_input = st.text_input("Anthropic API Key", type="password",
                                   placeholder="sk-ant-...", value=st.session_state.api_key)
        if key_input: st.session_state.api_key = key_input
    st.markdown('</div>', unsafe_allow_html=True)

    # Session Stats
    if st.session_state.agent:
        agent = st.session_state.agent
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-section-title">📊 Session Stats</div>', unsafe_allow_html=True)
        p_label = PERSONA_LABELS.get(agent.current_persona, "—")
        p_color = PERSONA_COLORS.get(agent.current_persona, "#a0aec0")
        conf_pct = int(agent.persona_confidence * 100)
        conf_color = score_color(agent.persona_confidence)
        stats = [
            ("Detected Persona", f'<span style="color:{p_color}">{p_label}</span>'),
            ("Confidence", f'<span style="color:{conf_color}">{conf_pct}%</span>'),
            ("Turn Count", str(agent.turn_count)),
            ("Status", '<span style="color:#fc8181">⚠️ Escalated</span>' if agent.is_escalated else '<span style="color:#68d391">✅ Active</span>'),
        ]
        if agent.last_confidence_scores:
            cs = agent.last_confidence_scores
            stats.append(("Response Confidence", f'<span style="color:{score_color(cs["overall"])}">{cs["label"]} ({cs["overall"]:.0%})</span>'))
        for label, value in stats:
            st.markdown(f'<div class="stat-row"><span class="stat-label">{label}</span><span class="stat-value">{value}</span></div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div style="margin-top:8px;">
            <div style="font-size:11px;color:#4a5568;margin-bottom:3px;">Persona confidence</div>
            <div class="conf-bar-bg"><div class="conf-bar-fill" style="width:{conf_pct}%;background:{conf_color};"></div></div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Persona Guide
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-section-title">👥 Personas</div>', unsafe_allow_html=True)
    for icon, name, color, desc in [
        ("🔧","Technical Expert","#63b3ed","Technical terms, logs, APIs"),
        ("😤","Frustrated User","#fc8181","Emotional, urgent requests"),
        ("💼","Business Executive","#68d391","ROI, SLA, business impact"),
    ]:
        st.markdown(f"""
        <div style="margin-bottom:8px;padding:8px;background:rgba(255,255,255,0.03);border-radius:6px;">
            <div style="font-size:13px;font-weight:600;color:{color};">{icon} {name}</div>
            <div style="font-size:11px;color:#4a5568;margin-top:2px;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Controls
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-section-title">⚙️ Controls</div>', unsafe_allow_html=True)
    if st.button("🔄 New Conversation", key="reset"):
        if st.session_state.agent: st.session_state.agent.reset_session()
        st.session_state.messages = []
        st.session_state.chat_input = ""
        st.session_state.pending_feedback = {}
        st.rerun()
    if st.button("🗑️ Rebuild Knowledge Base", key="rebuild"):
        if st.session_state.agent:
            with st.spinner("Rebuilding index..."):
                from src.agent import load_all_documents
                chunks = load_all_documents()
                st.session_state.agent.vector_store.build_index(chunks, force_rebuild=True)
            st.success("Index rebuilt!")
    st.markdown('</div>', unsafe_allow_html=True)

    # KB Info
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-section-title">📚 Knowledge Base</div>', unsafe_allow_html=True)
    data_dir = Path(__file__).parent / "data"
    if data_dir.exists():
        files = [f for f in data_dir.iterdir() if f.suffix in (".md", ".pdf")]
        md_count = sum(1 for f in files if f.suffix == ".md")
        pdf_count = sum(1 for f in files if f.suffix == ".pdf")
        for label, val in [("Documents", len(files)), ("Markdown", md_count), ("PDF", pdf_count)]:
            st.markdown(f'<div class="stat-row"><span class="stat-label">{label}</span><span class="stat-value">{val}</span></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ─── Header ───
st.markdown("""
<div class="header-banner">
    <div style="font-size:28px;">🤖</div>
    <div>
        <p class="header-title">CloudSync AI Support Agent</p>
        <p class="header-subtitle">Persona-Adaptive · RAG-Powered · Sentiment-Aware · Human Escalation</p>
    </div>
    <div class="header-status"><div class="status-dot"></div>AI Agent Online</div>
</div>
""", unsafe_allow_html=True)

has_api_key = bool(st.session_state.api_key or os.environ.get("ANTHROPIC_API_KEY"))
if not has_api_key:
    st.markdown("""
    <div class="welcome-card">
        <div class="welcome-icon">🔑</div>
        <div class="welcome-title">Configure Your API Key</div>
        <div class="welcome-sub">Enter your Anthropic API key in the sidebar to get started.<br>Get your key at <strong>console.anthropic.com</strong></div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

agent = get_agent()


# ════════════════════════════════════════════
#  ANALYTICS DASHBOARD TAB
# ════════════════════════════════════════════
if st.session_state.active_tab == "analytics":
    st.markdown("## 📊 Analytics Dashboard")

    if not agent:
        st.warning("Initialize the agent first by sending a message.")
        st.stop()

    analytics = agent.get_analytics()

    if not analytics or analytics.get("total_conversations", 0) == 0:
        st.info("No conversation data yet. Start chatting to see analytics here!")
        if st.button("← Back to Chat"):
            st.session_state.active_tab = "chat"
            st.rerun()
        st.stop()

    # KPI Row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Conversations", analytics.get("total_conversations", 0))
    with col2:
        st.metric("Total Sessions", analytics.get("total_sessions", 0))
    with col3:
        st.metric("Escalation Rate", f"{analytics.get('escalation_rate', 0)}%")
    with col4:
        avg_rating = analytics.get("avg_feedback_rating", 0)
        st.metric("Avg Rating", f"{'⭐' * int(round(avg_rating))} {avg_rating:.1f}/5" if avg_rating > 0 else "No ratings yet")

    st.markdown("---")

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("### 👥 Persona Distribution")
        persona_dist = analytics.get("persona_distribution", {})
        if persona_dist:
            labels = {"technical_expert": "🔧 Technical Expert", "frustrated_user": "😤 Frustrated User", "business_exec": "💼 Business Exec"}
            total = sum(persona_dist.values())
            for k, v in sorted(persona_dist.items(), key=lambda x: -x[1]):
                pct = v / total * 100
                label = labels.get(k, k)
                color = PERSONA_COLORS.get(k, "#a0aec0")
                st.markdown(f"""
                <div style="margin-bottom:12px;">
                    <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
                        <span style="color:{color};font-weight:600;font-size:13px;">{label}</span>
                        <span style="color:#a0aec0;font-size:13px;">{v} ({pct:.1f}%)</span>
                    </div>
                    <div style="background:rgba(255,255,255,0.08);border-radius:4px;height:6px;">
                        <div style="width:{pct}%;background:{color};height:6px;border-radius:4px;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("### 💬 Sentiment Distribution")
        sentiment_dist = analytics.get("sentiment_distribution", {})
        if sentiment_dist:
            sent_colors = {"positive": "#68d391", "negative": "#fc8181", "neutral": "#a0aec0"}
            sent_icons = {"positive": "😊", "negative": "😤", "neutral": "😐"}
            total = sum(sentiment_dist.values())
            for k, v in sorted(sentiment_dist.items(), key=lambda x: -x[1]):
                pct = v / total * 100
                color = sent_colors.get(k, "#a0aec0")
                icon = sent_icons.get(k, "😐")
                st.markdown(f"""
                <div style="margin-bottom:8px;">
                    <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
                        <span style="color:{color};font-size:13px;">{icon} {k.title()}</span>
                        <span style="color:#a0aec0;font-size:13px;">{v} ({pct:.1f}%)</span>
                    </div>
                    <div style="background:rgba(255,255,255,0.08);border-radius:4px;height:4px;">
                        <div style="width:{pct}%;background:{color};height:4px;border-radius:4px;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    with col_right:
        st.markdown("### 🎯 Quality Metrics")
        metrics = [
            ("Avg Persona Confidence", f"{analytics.get('avg_persona_confidence', 0):.1f}%", score_color(analytics.get('avg_persona_confidence', 0)/100)),
            ("Avg Retrieval Score", f"{analytics.get('avg_retrieval_score', 0):.1f}%", score_color(analytics.get('avg_retrieval_score', 0)/100)),
            ("Total Escalations", str(analytics.get("total_escalations", 0)), "#fc8181"),
            ("Total Feedback", str(analytics.get("total_feedback", 0)), "#68d391"),
        ]
        for label, value, color in metrics:
            st.markdown(f"""
            <div style="background:rgba(26,32,46,0.8);border:1px solid rgba(255,255,255,0.07);border-radius:10px;padding:16px;margin-bottom:10px;display:flex;justify-content:space-between;align-items:center;">
                <span style="color:#a0aec0;font-size:13px;">{label}</span>
                <span style="color:{color};font-size:18px;font-weight:700;">{value}</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("### 📅 Recent Activity (Last 7 Days)")
        daily = analytics.get("daily_volume", [])
        if daily:
            max_count = max(d["count"] for d in daily) or 1
            for d in reversed(daily):
                pct = d["count"] / max_count * 100
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
                    <span style="color:#718096;font-size:12px;width:80px;">{d['date']}</span>
                    <div style="flex:1;background:rgba(255,255,255,0.05);border-radius:4px;height:8px;">
                        <div style="width:{pct}%;background:#63b3ed;height:8px;border-radius:4px;"></div>
                    </div>
                    <span style="color:#63b3ed;font-size:12px;width:30px;text-align:right;">{d['count']}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No daily data yet")

    if st.button("← Back to Chat", key="back_to_chat"):
        st.session_state.active_tab = "chat"
        st.rerun()
    st.stop()


# ════════════════════════════════════════════
#  CHAT TAB
# ════════════════════════════════════════════

def render_message(msg: dict):
    role = msg["role"]
    content = msg["content"]
    ts = msg.get("timestamp", "")
    meta = msg.get("meta", {})

    if role == "user":
        st.markdown(f"""
        <div class="msg-user">
            <div>
                <div class="bubble-user">{content}</div>
                <div class="msg-time">{fmt_ts(ts)}</div>
            </div>
            <div class="avatar-user">👤</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        persona = meta.get("persona", "")
        persona_label = meta.get("persona_label", "")
        confidence = meta.get("persona_confidence", 0)
        sentiment = meta.get("sentiment", "")
        sentiment_label = meta.get("sentiment_label", "")
        conf_scores = meta.get("confidence_scores", {})

        badge_html = ""
        if persona:
            icon = PERSONA_ICONS.get(persona, "🤖")
            sent_class = f"sentiment-{sentiment}" if sentiment else ""
            sent_badge = f'<span class="sentiment-badge {sent_class}">{sentiment_label}</span>' if sentiment_label else ""
            badge_html = f'<div class="persona-badge persona-{persona}">{icon} {persona_label} · {confidence}% confidence{sent_badge}</div>'

        import html as html_lib
        safe = html_lib.escape(content).replace('\n', '<br>')

        # Confidence indicator
        conf_html = ""
        if conf_scores:
            overall = conf_scores.get("overall", 0)
            clabel = conf_scores.get("label", "")
            ccolor = score_color(overall)
            conf_html = f'<div style="font-size:10px;color:{ccolor};margin-top:4px;">🎯 Response confidence: {clabel} ({overall:.0%})</div>'

        st.markdown(f"""
        <div class="msg-agent">
            <div class="avatar-agent">🤖</div>
            <div style="flex:1;">
                {badge_html}
                <div class="bubble-agent">{safe}</div>
                {conf_html}
                <div class="msg-time">{fmt_ts(ts)}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Retrieved sources
        retrieved = meta.get("retrieved_docs", [])
        if retrieved:
            with st.expander(f"📚 {len(retrieved)} Knowledge Base Source(s)", expanded=False):
                for hit in retrieved:
                    sc = hit.get("score", 0)
                    sc_color = score_color(sc)
                    st.markdown(f"""
                    <div class="source-card">
                        <div class="source-card-header">
                            <span>📄</span>
                            <span class="source-name">{hit['source']}</span>
                            <span class="source-score" style="color:{sc_color};">⬤ {sc:.0%}</span>
                        </div>
                        <div class="source-section">§ {hit['section']}</div>
                    </div>
                    """, unsafe_allow_html=True)

        # Key facts
        key_facts = meta.get("key_facts", [])
        if key_facts:
            with st.expander("🧠 Extracted Context", expanded=False):
                for fact in key_facts:
                    st.markdown(f'<div style="font-size:12px;color:#a0aec0;padding:2px 0;">• {fact}</div>', unsafe_allow_html=True)

        # Escalation
        if meta.get("escalated"):
            reason = meta.get("escalation_reason", "")
            st.markdown(f"""
            <div class="escalation-banner">
                <div class="escalation-title">🚨 Escalated to Human Agent</div>
                <div class="escalation-reason">Reason: {reason}</div>
            </div>
            """, unsafe_allow_html=True)
            handoff = meta.get("handoff_summary")
            if handoff:
                with st.expander("📋 Human Handoff Summary", expanded=True):
                    st.markdown(f'<div class="handoff-card">{json.dumps(handoff, indent=2)}</div>', unsafe_allow_html=True)
                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button(
                            "⬇️ Download Handoff JSON",
                            data=json.dumps(handoff, indent=2),
                            file_name=f"handoff_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json",
                        )

        # Feedback
        turn_id = meta.get("turn_id", "")
        if turn_id and turn_id not in st.session_state.pending_feedback:
            with st.expander("⭐ Rate this response", expanded=False):
                fb_col1, fb_col2 = st.columns([3, 1])
                with fb_col1:
                    rating = st.slider("Rating", 1, 5, 4, key=f"rating_{turn_id}")
                    helpful = st.checkbox("Was this helpful?", value=True, key=f"helpful_{turn_id}")
                    comment = st.text_input("Comment (optional)", key=f"comment_{turn_id}", placeholder="Any feedback...")
                with fb_col2:
                    if st.button("Submit", key=f"fb_submit_{turn_id}"):
                        if agent:
                            ok = agent.submit_feedback(turn_id, rating, helpful, comment)
                            if ok:
                                st.session_state.pending_feedback[turn_id] = True
                                st.success("✅ Thanks for your feedback!")
                                time.sleep(0.5)
                                st.rerun()
        elif turn_id in st.session_state.pending_feedback:
            st.markdown('<div style="font-size:11px;color:#68d391;">✅ Feedback submitted</div>', unsafe_allow_html=True)


# Welcome screen
if not st.session_state.messages:
    st.markdown("""
    <div class="welcome-card">
        <div class="welcome-icon">💬</div>
        <div class="welcome-title">Welcome to CloudSync Support</div>
        <div class="welcome-sub">
            I'm your AI support assistant — I detect your communication style and adapt responses for you.<br>
            I analyze sentiment, track context across turns, and escalate to human agents when needed.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 💡 Try these example queries:")
    examples = [
        ("🔧 Technical", "Can you explain the OAuth 2.0 authentication flow and what causes 401 vs 403 errors in the API? I need to debug my integration."),
        ("😤 Frustrated", "I've been trying to reset my password for hours and NOTHING works!! The reset email never arrives and I'm completely locked out. This is ridiculous!"),
        ("💼 Executive", "Our team has been experiencing sync failures since this morning. What's the business impact and when can we expect resolution?"),
        ("🔧 Technical", "How do I configure webhook signature verification? What HMAC algorithm does CloudSync use and how do I handle retry logic?"),
        ("😤 Frustrated", "I can't believe this! My data isn't syncing and I have a presentation in 2 hours. I've already tried restarting everything!"),
        ("💼 Executive", "What are the SLA commitments for our Business plan and how do we claim service credits for the downtime we experienced?"),
    ]

    def _example_click(q):
        st.session_state.chat_input = q
        st.session_state.example_query = q
        st.session_state.auto_send = True

    cols = st.columns(3)
    for i, (label, query) in enumerate(examples):
        with cols[i % 3]:
            st.button(f"{label}\n{query[:55]}...", key=f"ex_{i}", help=query,
                      on_click=_example_click, args=(query,), use_container_width=True)

# Render chat history
if st.session_state.messages:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for msg in st.session_state.messages:
        render_message(msg)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

# Input area
st.markdown("---")
prefill = st.session_state.get("chat_input", "")
col_input, col_btn = st.columns([5, 1])

with col_input:
    user_input = st.text_area(
        "Message", value=prefill,
        placeholder="Describe your issue or ask a question...",
        height=80, label_visibility="collapsed", key="chat_input",
    )

with col_btn:
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    send_btn = st.button("➤ Send", key="send", use_container_width=True)

auto_send = st.session_state.get("auto_send", False)
send_trigger = send_btn or auto_send

if send_trigger and user_input.strip():
    st.session_state.auto_send = False
    st.session_state.example_query = None

    user_msg = {
        "role": "user",
        "content": user_input.strip(),
        "timestamp": datetime.now().isoformat(),
        "meta": {},
    }
    st.session_state.messages.append(user_msg)

    with st.spinner("🤖 Thinking..."):
        try:
            if agent:
                result = agent.chat(user_input.strip())
            else:
                raise RuntimeError("Agent not initialized. Please enter your API key.")

            agent_msg = {
                "role": "assistant",
                "content": result["response"],
                "timestamp": datetime.now().isoformat(),
                "meta": {
                    "persona": result.get("persona", ""),
                    "persona_label": result.get("persona_label", ""),
                    "persona_confidence": result.get("persona_confidence", 0),
                    "sentiment": result.get("sentiment", "neutral"),
                    "sentiment_label": result.get("sentiment_label", ""),
                    "retrieved_docs": result.get("retrieved_docs", []),
                    "escalated": result.get("escalated", False),
                    "escalation_reason": result.get("escalation_reason", ""),
                    "handoff_summary": result.get("handoff_summary"),
                    "confidence_scores": result.get("confidence_scores", {}),
                    "key_facts": result.get("key_facts", []),
                    "turn_id": result.get("id", ""),
                },
            }
            st.session_state.messages.append(agent_msg)
        except Exception as e:
            st.error(f"Error: {e}")

    st.rerun()

st.markdown("""
<div style="text-align:center;margin-top:20px;padding:12px;border-top:1px solid rgba(255,255,255,0.05);">
    <span style="font-size:11px;color:#2d3748;">
        CloudSync AI Support · Claude claude-sonnet-4-6 · RAG + ChromaDB · Persona-Adaptive · Sentiment Analysis · Analytics
    </span>
</div>
""", unsafe_allow_html=True)
