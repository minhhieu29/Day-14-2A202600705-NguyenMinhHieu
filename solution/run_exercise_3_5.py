import os
import sys

# Add solution folder to path
solution_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "solution")
sys.path.append(solution_dir)
from solution import RAGASEvaluator, rerank_by_overlap

def run():
    dataset = [
        {
            "id": "R01",
            "question": "What is the capital of France?",
            "expected": "Paris is the capital of France",
            "chunks": [
                "Bananas are a tropical fruit.",
                "The Eiffel Tower is in Paris.",
                "Paris is the capital city of France."
            ]
        },
        {
            "id": "R02",
            "question": "What does RAG stand for?",
            "expected": "RAG stands for Retrieval-Augmented Generation",
            "chunks": [
                "LLMs can hallucinate facts.",
                "Retrieval-Augmented Generation (RAG) combines retrieval with generation.",
                "Vector databases store embeddings."
            ]
        },
        {
            "id": "R03",
            "question": "When was the Eiffel Tower built?",
            "expected": "The Eiffel Tower was completed in 1889",
            "chunks": [
                "The tower is 330 metres tall.",
                "It is made of wrought iron.",
                "The Eiffel Tower was completed in 1889 for the World's Fair."
            ]
        },
        {
            "id": "R04",
            "question": "What is gradient descent?",
            "expected": "Gradient descent minimizes a loss function by following the negative gradient",
            "chunks": [
                "Neural networks have layers.",
                "Gradient descent updates weights along the negative gradient to minimize loss.",
                "Learning rate controls step size."
            ]
        },
        {
            "id": "R05",
            "question": "What is overfitting?",
            "expected": "Overfitting is when a model memorizes training data and fails to generalize",
            "chunks": [
                "Regularization adds a penalty term.",
                "Dropout randomly disables neurons.",
                "Overfitting means the model memorizes training data and generalizes poorly."
            ]
        }
    ]

    ev = RAGASEvaluator()
    print("=== EXERCISE 3.5 RESULTS ===")
    print("\n--- Part 2 & 3: Recall and Precision before/after rerank ---")
    print("| ID | Context Recall | Context Precision (before) | Precision (after rerank) | Delta |")
    print("|----|----------------|----------------------------|--------------------------|-------|")
    
    recalls = []
    precisions_before = []
    precisions_after = []
    
    for row in dataset:
        rid = row["id"]
        q = row["question"]
        expected = row["expected"]
        chunks = row["chunks"]
        
        recall = ev.evaluate_context_recall(chunks, expected)
        prec_before = ev.evaluate_context_precision(chunks, expected)
        
        # Rerank by query (which is the question)
        reranked = rerank_by_overlap(chunks, q)
        prec_after = ev.evaluate_context_precision(reranked, expected)
        
        delta = prec_after - prec_before
        
        recalls.append(recall)
        precisions_before.append(prec_before)
        precisions_after.append(prec_after)
        
        print(f"| {rid} | {recall:.4f} | {prec_before:.4f} | {prec_after:.4f} | {delta:+.4f} |")
        
    avg_recall = sum(recalls) / len(recalls)
    avg_prec_before = sum(precisions_before) / len(precisions_before)
    avg_prec_after = sum(precisions_after) / len(precisions_after)
    avg_delta = avg_prec_after - avg_prec_before
    print(f"| **Avg** | {avg_recall:.4f} | {avg_prec_before:.4f} | {avg_prec_after:.4f} | {avg_delta:+.4f} |")

if __name__ == "__main__":
    run()
