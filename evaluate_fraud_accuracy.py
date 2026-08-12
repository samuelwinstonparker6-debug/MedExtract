"""
evaluate_fraud_accuracy.py

Evaluates the MedExtract fraud detection pipeline against the labeled dataset
produced by build_fraud_dataset.py.

Runs every comparison pair from tests/fraud_dataset/labels.json through the
fingerprinting + similarity pipeline and reports:
  - True Positive Rate  (TPR): fraud pairs correctly flagged AMBER or RED
  - False Positive Rate (FPR): genuine pairs incorrectly flagged
  - Overall Accuracy          : (TP + TN) / total pairs

This is the primary accuracy metric for the README and any presentation, directly
answering the problem statement's "accuracy of detection" evaluation criterion.

Usage:
    python evaluate_fraud_accuracy.py
    python evaluate_fraud_accuracy.py --dataset tests/fraud_dataset
"""

import sys
import json
import argparse
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from app.services.template_extractor import generate_fingerprint
from app.services.template_matcher import calculate_similarity, evaluate_fraud, get_thresholds_for_type


def run_evaluation(dataset_dir: Path) -> dict:
    labels_file = dataset_dir / "labels.json"
    if not labels_file.exists():
        print(f"[ERROR] labels.json not found at {labels_file}")
        print("  Run:  python build_fraud_dataset.py  first.")
        sys.exit(1)

    with open(labels_file) as f:
        data = json.load(f)

    # Support both "pairs" format (from existing build_fraud_dataset.py)
    # and "entries" format (from our rewritten version)
    pair_entries = data.get("pairs", data.get("entries", []))
    pair_entries = [e for e in pair_entries if "file_a" in e or "pair" in e]

    if not pair_entries:
        print("[ERROR] No evaluation pairs found in labels.json")
        sys.exit(1)

    print()
    print("=" * 70)
    print("  MedExtract Fraud Detection Accuracy Evaluation")
    print("=" * 70)
    print(f"  Dataset : {dataset_dir.resolve()}")
    print(f"  Pairs   : {len(pair_entries)}")
    print("=" * 70)
    print()

    results = []

    for entry in pair_entries:
        # Support both format styles (pair-list and file_a/file_b)
        if "pair" in entry:
            file_a_rel, file_b_rel = entry["pair"]
        else:
            file_a_rel = entry["file_a"]
            file_b_rel = entry["file_b"]

        # Read provider names directly from the entry (populated by build_fraud_dataset.py)
        provider_a = entry.get("provider_a", "")
        provider_b = entry.get("provider_b", "")

        label      = entry.get("label", "genuine")     # "fraud" | "genuine"
        doc_type   = entry.get("doc_type", "")
        description = entry.get("description", f"{file_a_rel} vs {file_b_rel}")

        file_a = dataset_dir / file_a_rel
        file_b = dataset_dir / file_b_rel

        if not file_a.exists() or not file_b.exists():
            print(f"  [SKIP] Missing files: {file_a_rel} or {file_b_rel}")
            continue

        # Generate full fingerprints (phash + boxes + color_hist)
        try:
            fp_a = generate_fingerprint(str(file_a))
            fp_b = generate_fingerprint(str(file_b))
        except Exception as e:
            print(f"  [ERROR] Fingerprint failed: {e}")
            continue

        score = calculate_similarity(fp_a, fp_b)

        # evaluate_fraud respects same-provider logic: same provider -> NONE always
        detected = evaluate_fraud(score, provider_a, provider_b, doc_type)
        flagged = detected in ("AMBER", "RED")
        amber_thresh, red_thresh = get_thresholds_for_type(doc_type)

        # Classify outcome
        if label == "fraud":
            outcome = "TP" if flagged else "FN"
            is_correct = flagged
        else:
            outcome = "TN" if not flagged else "FP"
            is_correct = not flagged

        results.append({
            "pair": [file_a_rel, file_b_rel],
            "doc_type": doc_type,
            "label": label,
            "score": round(score, 4),
            "detected": detected,
            "outcome": outcome,
            "is_correct": is_correct,
            "description": description,
            "amber_thresh": amber_thresh,
            "red_thresh": red_thresh,
        })

        mark = "[OK]" if is_correct else "[!!]"
        print(f"  {mark} [{outcome}] {doc_type:<14} score={score:.3f} "
              f"thresh(a>{amber_thresh}/r>{red_thresh}) flag={detected} | {label}")
        print(f"       {description}")
        print()

    # ── Aggregate metrics ──────────────────────────────────────────────────────
    fraud_results   = [r for r in results if r["label"] == "fraud"]
    genuine_results = [r for r in results if r["label"] == "genuine"]

    tp = sum(1 for r in fraud_results   if r["outcome"] == "TP")
    fn = sum(1 for r in fraud_results   if r["outcome"] == "FN")
    tn = sum(1 for r in genuine_results if r["outcome"] == "TN")
    fp = sum(1 for r in genuine_results if r["outcome"] == "FP")

    total   = len(results)
    correct = tp + tn

    tpr      = tp / len(fraud_results)   if fraud_results   else 0.0
    fpr      = fp / len(genuine_results) if genuine_results else 0.0
    accuracy = correct / total           if total           else 0.0

    doc_types = sorted(set(r["doc_type"] for r in results))

    print()
    print("=" * 70)
    print("  RESULTS SUMMARY")
    print("=" * 70)
    print()
    print("  Confusion Matrix:")
    print(f"    True  Positives (fraud correctly flagged)  : {tp:3d}")
    print(f"    False Negatives (fraud missed)             : {fn:3d}")
    print(f"    True  Negatives (genuine correctly cleared): {tn:3d}")
    print(f"    False Positives (genuine wrongly flagged)  : {fp:3d}")
    print()
    print(f"  True Positive Rate  (TPR)  : {tpr*100:6.1f}%")
    print(f"  False Positive Rate (FPR)  : {fpr*100:6.1f}%")
    print(f"  Overall Accuracy           : {accuracy*100:6.1f}%")
    print()
    print(f"  Per Document-Type Breakdown:")
    print(f"  {'Doc Type':<16}  {'TPR':>6}  {'FPR':>6}  {'Accuracy':>9}")
    print(f"  {'-'*46}")

    per_type = {}
    for dt in doc_types:
        dt_all     = [r for r in results if r["doc_type"] == dt]
        dt_fraud   = [r for r in dt_all  if r["label"] == "fraud"]
        dt_genuine = [r for r in dt_all  if r["label"] == "genuine"]
        dt_tp = sum(1 for r in dt_fraud   if r["outcome"] == "TP")
        dt_fp = sum(1 for r in dt_genuine if r["outcome"] == "FP")
        dt_tn = sum(1 for r in dt_genuine if r["outcome"] == "TN")
        dt_tpr = dt_tp / len(dt_fraud)   if dt_fraud   else 0.0
        dt_fpr = dt_fp / len(dt_genuine) if dt_genuine else 0.0
        dt_acc = (dt_tp + dt_tn) / len(dt_all) if dt_all else 0.0
        per_type[dt] = {"tpr": dt_tpr, "fpr": dt_fpr, "accuracy": dt_acc}
        print(f"  {dt:<16}  {dt_tpr*100:>5.1f}%  {dt_fpr*100:>5.1f}%  {dt_acc*100:>8.1f}%")

    print()

    # Save JSON report
    report_path = dataset_dir / "accuracy_report.json"
    report = {
        "total_pairs": total,
        "TP": tp, "FN": fn, "TN": tn, "FP": fp,
        "true_positive_rate":  round(tpr,      4),
        "false_positive_rate": round(fpr,      4),
        "overall_accuracy":    round(accuracy, 4),
        "per_doc_type": {dt: {k: round(v, 4) for k, v in m.items()} for dt, m in per_type.items()},
        "pair_results": results,
    }
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"  Report saved to: {report_path.resolve()}")
    print("=" * 70)
    print()

    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate MedExtract fraud detection accuracy")
    parser.add_argument("--dataset", default="tests/fraud_dataset",
                        help="Path to fraud dataset directory (default: tests/fraud_dataset)")
    args = parser.parse_args()
    run_evaluation(Path(args.dataset))
