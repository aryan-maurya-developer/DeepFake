from __future__ import annotations

import math
from typing import Any

import numpy as np


DEFAULT_MODEL_WEIGHTS = {
    "image": {
        "npr_deepfakedetection": 1.05,
        "universalfakedetect": 1.15,
    },
    "video": {
        "cross_efficient_vit": 1.15,
    },
    "audio": {
        "vocoder_artifacts": 1.1,
    },
}


def summarize_quality(preprocess_metadata: dict[str, Any] | None) -> float:
    if not preprocess_metadata:
        return 0.5
    return float(preprocess_metadata.get("quality_score", 0.5))


def build_confidence(probability: float, agreement: float, quality_score: float) -> float:
    margin = abs(probability - 0.5) * 2.0
    confidence = (0.5 * margin) + (0.3 * agreement) + (0.2 * quality_score)
    return max(0.05, min(0.99, confidence))


def calculate_improved_ensemble(
    results: dict[str, dict[str, Any]],
    threshold: float,
    method: str,
    media_type: str,
    stacking_probability: float | None = None,
    preprocess_metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    valid_results = {
        name: result
        for name, result in results.items()
        if isinstance(result, dict)
        and "error" not in result
        and result.get("probability") is not None
    }
    if not valid_results:
        return {
            "verdict": "undetermined",
            "confidence": 0.0,
            "probability": 0.5,
            "fake_votes": 0,
            "real_votes": 0,
            "actual_method_used": method,
            "agreement_score": 0.0,
            "quality_score": summarize_quality(preprocess_metadata),
            "weighted_scores": {},
        }

    quality_score = summarize_quality(preprocess_metadata)
    weights = DEFAULT_MODEL_WEIGHTS.get(media_type, {})
    weighted_scores: dict[str, float] = {}
    probabilities: list[float] = []
    weighted_sum = 0.0
    weight_total = 0.0
    fake_votes = 0
    real_votes = 0

    for name, result in valid_results.items():
        probability = float(result["probability"])
        probabilities.append(probability)
        if probability >= threshold:
            fake_votes += 1
        else:
            real_votes += 1
        confidence_hint = abs(probability - 0.5) * 2.0
        model_weight = weights.get(name, 1.0) * (0.8 + (confidence_hint * 0.4))
        weighted_scores[name] = model_weight
        weighted_sum += probability * model_weight
        weight_total += model_weight

    weighted_average = weighted_sum / weight_total if weight_total else 0.5
    vote_probability = fake_votes / max(1, fake_votes + real_votes)
    agreement_score = 1.0 - min(1.0, float(np.std(probabilities)) * 2.0) if len(probabilities) > 1 else 1.0

    actual_method_used = method
    if method == "stacking" and stacking_probability is not None:
        combined_probability = (stacking_probability * 0.55) + (weighted_average * 0.30) + (vote_probability * 0.15)
    elif method == "average":
        combined_probability = weighted_average
    else:
        actual_method_used = "weighted_voting"
        combined_probability = (weighted_average * 0.7) + (vote_probability * 0.3)

    threshold_adjustment = 0.0
    if quality_score < 0.35 and combined_probability >= threshold:
        threshold_adjustment = 0.03
    if agreement_score < 0.4:
        threshold_adjustment += 0.02
    effective_threshold = min(0.95, max(0.05, threshold + threshold_adjustment))

    verdict = "fake" if combined_probability >= effective_threshold else "real"
    confidence = build_confidence(combined_probability, agreement_score, quality_score)
    false_positive_risk = max(0.0, min(1.0, (1.0 - agreement_score) * 0.6 + (1.0 - quality_score) * 0.4))

    return {
        "verdict": verdict,
        "confidence": confidence,
        "probability": max(0.0, min(1.0, combined_probability)),
        "fake_votes": fake_votes,
        "real_votes": real_votes,
        "actual_method_used": actual_method_used,
        "agreement_score": agreement_score,
        "quality_score": quality_score,
        "effective_threshold": effective_threshold,
        "false_positive_risk": false_positive_risk,
        "weighted_scores": weighted_scores,
    }
