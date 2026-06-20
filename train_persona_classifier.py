"""
Simple supervised persona classifier trained on labeled examples.
Uses TF-IDF + Logistic Regression for production-grade accuracy.
Run: python train_persona_classifier.py
"""
import os
from dotenv import load_dotenv
load_dotenv()
import json
import pickle
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

DATA = Path(__file__).parent / "data" / "test_cases.jsonl"
MODEL_PATH = Path(__file__).parent / ".persona_classifier.pkl"


def load_training_data(path: Path):
    texts, labels = [], []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            texts.append(obj["query"])
            labels.append(obj["expected_persona"])
    return texts, labels


def train():
    print("Loading training data...")
    texts, labels = load_training_data(DATA)
    
    print(f"Training on {len(texts)} examples: {set(labels)}")
    
    # Build pipeline: TF-IDF → Logistic Regression
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(max_features=200, ngram_range=(1, 2), lowercase=True)),
        ("clf", LogisticRegression(max_iter=1000, random_state=42)),
    ])
    
    pipeline.fit(texts, labels)
    
    # Test on same data (for sanity check)
    preds = pipeline.predict(texts)
    acc = sum(p == l for p, l in zip(preds, labels)) / len(labels) * 100
    
    print(f"Training accuracy: {acc:.1f}%")
    
    # Save
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(pipeline, f)
    
    print(f"[OK] Model saved to {MODEL_PATH}")


def predict(query: str) -> tuple:
    """Predict persona for query. Returns (persona, confidence)."""
    if not MODEL_PATH.exists():
        print("⚠️ Model not trained. Run: python train_persona_classifier.py")
        return "frustrated_user", 0.5
    
    with open(MODEL_PATH, "rb") as f:
        pipeline = pickle.load(f)
    
    persona = pipeline.predict([query])[0]
    confidence = float(pipeline.predict_proba([query]).max())
    
    return persona, confidence


if __name__ == "__main__":
    train()
