#!/usr/bin/env python3
"""
CloudSync AI Support Agent — Enhanced CLI
Features: Persona Detection, Sentiment Analysis, Confidence Scoring,
Multi-turn Memory, Escalation, Feedback Collection, Analytics
Run: python cli.py
"""

import os
import sys
import json
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(__file__))


def colored(text, code):
    return f"\033[{code}m{text}\033[0m"

def blue(t):    return colored(t, "94")
def green(t):   return colored(t, "92")
def red(t):     return colored(t, "91")
def yellow(t):  return colored(t, "93")
def cyan(t):    return colored(t, "96")
def bold(t):    return colored(t, "1")
def dim(t):     return colored(t, "2")


SENTIMENT_ICONS = {"positive": "😊", "negative": "😤", "neutral": "😐"}
CONF_COLORS = {"High": green, "Medium": yellow, "Low": red}


def print_separator(char="─", width=65):
    print(dim(char * width))

def print_double_sep(width=65):
    print(bold("═" * width))


def format_source_line(doc):
    """Format a retrieved source line safely without nested f-string issues."""
    source = doc.get("source", "")
    section = doc.get("section", "")
    score = doc.get("score", 0)
    score_pct = f"{score:.0%}"
    label = "High" if score >= 0.7 else ("Medium" if score >= 0.45 else "Low")
    color_fn = CONF_COLORS.get(label, dim)
    return f"   \u2022 {source} \u203a {section}  [{color_fn(score_pct)}]"


def main():
    print_double_sep()
    print(bold("  \U0001f916  CloudSync AI Support Agent  (CLI Mode)"))
    print(bold("  Powered by Claude \u00b7 RAG \u00b7 Persona-Adaptive \u00b7 Sentiment Analysis"))
    print_double_sep()

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        api_key = input("\n" + yellow("🔑 Enter your Anthropic API key: ")).strip()
    if not api_key:
        print(red("❌ API key required. Exiting."))
        sys.exit(1)

    print("\n" + yellow("⏳ Initializing agent and loading knowledge base..."))
    from src.agent import SupportAgent, PERSONA_LABELS
    agent = SupportAgent(api_key=api_key)
    print(green("✅ Agent ready!") + " (Type " + cyan("help") + " for commands)\n")

    print_separator()
    print("  " + bold("Commands: ") + cyan("quit") + " · " + cyan("reset") + " · " + cyan("feedback") + " · " + cyan("analytics") + " · " + cyan("help"))
    print_separator()
    print()

    last_turn_id = None

    while True:
        try:
            user_input = input(blue("You") + ": ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n" + yellow("👋 Goodbye!"))
            break

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit", "bye"):
            print("\n" + yellow("👋 Goodbye!"))
            break

        if user_input.lower() == "reset":
            agent.reset_session()
            last_turn_id = None
            print(green("🔄 Session reset. New conversation started.") + "\n")
            continue

        if user_input.lower() == "help":
            print("\n" + bold("Available commands:"))
            print("  " + cyan("reset")     + "     — Start a new conversation")
            print("  " + cyan("feedback")  + "  — Rate the last response")
            print("  " + cyan("analytics") + " — View session analytics")
            print("  " + cyan("quit")      + "      — Exit the agent\n")
            continue

        if user_input.lower() == "analytics":
            data = agent.get_analytics()
            if not data or data.get("total_conversations", 0) == 0:
                print(yellow("📊 No analytics data yet. Start chatting!") + "\n")
            else:
                print("\n" + bold("📊 Analytics Summary"))
                print_separator()
                print("  Total Conversations : " + str(data.get("total_conversations", 0)))
                print("  Total Sessions      : " + str(data.get("total_sessions", 0)))
                print("  Escalation Rate     : " + str(data.get("escalation_rate", 0)) + "%")
                print("  Avg Confidence      : " + str(data.get("avg_persona_confidence", 0)) + "%")
                print("  Avg Retrieval Score : " + str(data.get("avg_retrieval_score", 0)) + "%")
                avg_r = data.get("avg_feedback_rating", 0)
                print("  Avg Feedback Rating : " + (str(round(avg_r, 1)) + "/5" if avg_r else "No ratings yet"))
                pd = data.get("persona_distribution", {})
                if pd:
                    print("\n  " + bold("Persona Distribution:"))
                    for k, v in pd.items():
                        label = PERSONA_LABELS.get(k, k)
                        print("    " + label + ": " + str(v))
                print()
            continue

        if user_input.lower() == "feedback":
            if not last_turn_id:
                print(yellow("⚠️  No recent turn to rate.") + "\n")
                continue
            try:
                rating_str = input("  " + cyan("Rating (1-5): ")).strip()
                rating = int(rating_str)
                helpful_str = input("  " + cyan("Was it helpful? (y/n): ")).strip().lower()
                helpful = helpful_str in ("y", "yes")
                comment = input("  " + cyan("Comment (optional): ")).strip()
                ok = agent.submit_feedback(last_turn_id, rating, helpful, comment)
                if ok:
                    print("  " + green("✅ Feedback submitted! Thank you.") + "\n")
                else:
                    print("  " + red("❌ Failed to submit feedback.") + "\n")
            except (ValueError, KeyboardInterrupt):
                print("  " + yellow("Feedback cancelled.") + "\n")
            continue

        # Process chat message
        result = agent.chat(user_input)
        last_turn_id = result.get("id", "")

        print()
        print_separator()

        # Persona + sentiment header
        persona_label = result["persona_label"]
        conf = result["persona_confidence"]
        sentiment = result.get("sentiment", "neutral")
        sent_icon = SENTIMENT_ICONS.get(sentiment, "😐")
        sentiment_label = result.get("sentiment_label", sentiment)
        conf_scores = result.get("confidence_scores", {})
        conf_label = conf_scores.get("label", "")
        conf_fn = CONF_COLORS.get(conf_label, dim)

        print("  " + bold(persona_label) + " · " + yellow(str(conf) + "% confidence") + "  " + sent_icon + " " + dim(sentiment_label))
        if conf_scores:
            overall_pct = int(conf_scores.get("overall", 0) * 100)
            print("  🎯 Response confidence: " + conf_fn(conf_label + " (" + str(overall_pct) + "%)"))
        print_separator()

        # Response text
        print("\n" + green("Agent") + ": " + result["response"] + "\n")

        # Retrieved sources
        if result.get("retrieved_docs"):
            print(cyan("📚 Sources used:"))
            for doc in result["retrieved_docs"][:3]:
                print(format_source_line(doc))
            print()

        # Key facts from memory
        facts = result.get("key_facts", [])
        if facts:
            print(dim("🧠 Context: " + ", ".join(facts[:3])) + "\n")

        # Escalation
        if result.get("escalated"):
            print(red("🚨 ESCALATED") + ": " + result.get("escalation_reason", ""))
            handoff = result.get("handoff_summary")
            if handoff:
                print("\n" + bold("📋 Human Handoff Summary:"))
                print(json.dumps(handoff, indent=2))
            print()

        print(dim("(type feedback to rate this response)") + "\n")


if __name__ == "__main__":
    main()
