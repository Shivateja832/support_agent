"""
Load test for 1k-2k concurrent users (simulated).
Run: python load_test.py
"""
import os
from dotenv import load_dotenv
load_dotenv()
import time
import threading
from collections import defaultdict
from src.agent import SupportAgent

NUM_USERS = 50  # Simulate concurrent users (lower for local testing)
QUERIES_PER_USER = 4  # Queries per user
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# Test queries (varied personas)
TEST_QUERIES = [
    "Can you help me reset my password? I've tried everything!",
    "How do I configure OAuth 2.0 for my API integration?",
    "What's the SLA for our Business plan?",
    "The system isn't syncing and I'm losing data!",
]

results = {"success": 0, "error": 0, "total_time": 0, "avg_latency": 0}
latencies = []
lock = threading.Lock()


def simulate_user(user_id: int, agent: SupportAgent):
    """Simulate a single user making multiple queries."""
    for i, query in enumerate(TEST_QUERIES):
        try:
            start = time.time()
            result = agent.chat(query)
            latency = time.time() - start
            
            with lock:
                latencies.append(latency)
                results["success"] += 1
                results["total_time"] += latency
            
            status = "[OK]" if result["response"] else "[WARN]"
            print(f"{status} User {user_id} Query {i+1}: {latency:.2f}s")
        except Exception as e:
            with lock:
                results["error"] += 1
            print(f"[ERR] User {user_id} Query {i+1}: {e}")


def main():
    if not API_KEY:
        print("[ERR] ANTHROPIC_API_KEY not set")
        return
    
    print(f"[INFO] Load test: {NUM_USERS} users x {QUERIES_PER_USER} queries = {NUM_USERS * QUERIES_PER_USER} total")
    print("[INFO] Initializing agent...")
    
    agent = SupportAgent(api_key=API_KEY)
    
    print("[INFO] Spawning user threads...\n")
    threads = []
    start_total = time.time()
    
    for user_id in range(NUM_USERS):
        t = threading.Thread(target=simulate_user, args=(user_id, agent))
        t.start()
        threads.append(t)
    
    for t in threads:
        t.join()
    
    total_time = time.time() - start_total
    
    # Summary
    print(f"\n{'='*60}")
    print("[SUMMARY] Load Test Results")
    print(f"{'='*60}")
    print(f"Total Users: {NUM_USERS}")
    print(f"Queries per User: {QUERIES_PER_USER}")
    print(f"Total Queries: {NUM_USERS * QUERIES_PER_USER}")
    print(f"Success: {results['success']}")
    print(f"Errors: {results['error']}")
    print(f"Wall Time: {total_time:.2f}s")
    
    if latencies:
        avg_lat = sum(latencies) / len(latencies)
        min_lat = min(latencies)
        max_lat = max(latencies)
        print(f"Avg Latency: {avg_lat:.2f}s")
        print(f"Min Latency: {min_lat:.2f}s")
        print(f"Max Latency: {max_lat:.2f}s")
        throughput = len(latencies) / total_time
        print(f"Throughput: {throughput:.2f} queries/sec")
    
    print(f"\n[OK] Load test complete")


if __name__ == "__main__":
    main()
