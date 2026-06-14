#!/usr/bin/env python3
from __future__ import annotations
"""
RAG Verifier Evaluation Benchmark

Computes Precision, Recall, and F1 scores for the RAG claim verification pipeline
against a human-curated ground truth (Robert's evidence ledger).
"""

import json
import argparse
from pathlib import Path
from sklearn.metrics import precision_recall_fscore_support, accuracy_score

def evaluate_predictions(predictions_file: Path, ground_truth_file: Path, output_file: Path):
    with open(predictions_file, 'r') as f:
        predictions_data = json.load(f)
        
    with open(ground_truth_file, 'r') as f:
        ground_truth_data = json.load(f)
        
    # Create lookup map for ground truth
    truth_map = {item['id']: item['classification'] for item in ground_truth_data}
    
    y_true = []
    y_pred = []
    
    for pred in predictions_data:
        claim_id = pred['id']
        if claim_id in truth_map:
            y_pred.append(pred['classification'])
            y_true.append(truth_map[claim_id])
            
    if not y_true:
        print("No matching claims found between predictions and ground truth.")
        return
        
    # Calculate metrics
    labels = ["Supported", "Contradicted", "Nuanced", "Unsupported"]
    precision, recall, f1, support = precision_recall_fscore_support(
        y_true, y_pred, labels=labels, zero_division=0
    )
    accuracy = accuracy_score(y_true, y_pred)
    
    metrics = {
        "overall_accuracy": accuracy,
        "classes": {}
    }
    
    for i, label in enumerate(labels):
        metrics["classes"][label] = {
            "precision": float(precision[i]),
            "recall": float(recall[i]),
            "f1": float(f1[i]),
            "support": int(support[i])
        }
        
    with open(output_file, 'w') as f:
        json.dump(metrics, f, indent=2)
        
    print(f"Evaluation complete. Accuracy: {accuracy:.2f}")
    print(f"Metrics saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate RAG Pipeline")
    parser.add_argument("--predictions", type=Path, required=True, help="RAG results JSON")
    parser.add_argument("--truth", type=Path, required=True, help="Ground truth JSON")
    parser.add_argument("--output", type=Path, required=True, help="Output metrics JSON")
    args = parser.parse_args()
    
    evaluate_predictions(args.predictions, args.truth, args.output)
