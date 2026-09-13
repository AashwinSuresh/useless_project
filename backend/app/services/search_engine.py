import re
from typing import Any, Dict, List
from app.schemas.search import SearchResult

TIER_METADATA = [
    {"tier": 1, "title": "Mundane Reality", "default_absurdity": 0.12},
    {"tier": 2, "title": "Mild Paranoia", "default_absurdity": 0.35},
    {"tier": 3, "title": "Overanalyzed Vortex", "default_absurdity": 0.58},
    {"tier": 4, "title": "Conspiracy Grade", "default_absurdity": 0.81},
    {"tier": 5, "title": "Multiverse Catastrophe", "default_absurdity": 0.96},
]


def normalize_probabilities(raw_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Guarantees exactly 5 items with valid integer probabilities strictly summing to 100
    using the Largest Remainder (Hare-Niemeyer) method.
    """
    results = list(raw_results)

    # Pad if fewer than 5 items
    default_placeholders = [
        "The situation resolved itself naturally with zero secondary motives.",
        "They briefly considered alternatives, hesitated, and returned to default behavior.",
        "An unspoken social protocol was breached, starting an invisible cycle of doubt.",
        "A clandestine focus group is taking notes on your real-time emotional response.",
        "Spacetime fluctuated by 0.0003 picoseconds, swapping you with an identical parallel version."
    ]

    while len(results) < 5:
        idx = len(results)
        results.append({
            "text": default_placeholders[idx],
            "probability": 5 - idx
        })

    results = results[:5]

    # Extract non-negative integer probabilities
    raw_probs = []
    for item in results:
        p = item.get("probability", 0)
        try:
            val = int(p)
        except (ValueError, TypeError):
            val = 0
        raw_probs.append(max(0, val))

    total = sum(raw_probs)
    if total <= 0:
        default_distribution = [40, 27, 18, 10, 5]
        for i in range(5):
            results[i]["probability"] = default_distribution[i]
        return results

    if total == 100:
        for i in range(5):
            results[i]["probability"] = raw_probs[i]
        return results

    # Largest remainder scaling
    scaled = [(p / total) * 100.0 for p in raw_probs]
    floored = [int(x) for x in scaled]
    remainder = 100 - sum(floored)

    diffs = [(scaled[i] - floored[i], i) for i in range(5)]
    diffs.sort(key=lambda x: x[0], reverse=True)

    for k in range(remainder):
        idx = diffs[k][1]
        floored[idx] += 1

    for i in range(5):
        results[i]["probability"] = floored[i]

    return results


def process_search_results(raw_items: List[Dict[str, Any]]) -> List[SearchResult]:
    """
    Validates, normalizes probabilities, assigns tiers and clean absurdity floats.
    """
    normalized = normalize_probabilities(raw_items)
    results: List[SearchResult] = []

    for i, item in enumerate(normalized):
        meta = TIER_METADATA[i]
        rank = i + 1

        # Absurdity validation (0.0 to 1.0)
        raw_abs = item.get("absurdity")
        try:
            absurdity_val = round(float(raw_abs), 2)
            if not (0.0 <= absurdity_val <= 1.0):
                absurdity_val = meta["default_absurdity"]
        except (TypeError, ValueError):
            absurdity_val = meta["default_absurdity"]

        text = str(item.get("text", "")).strip()
        if not text:
            text = f"Alternative explanation #{rank} regarding the universe's quiet indifference."

        results.append(
            SearchResult(
                rank=rank,
                tier=meta["tier"],
                title=meta["title"],
                text=text,
                probability=item["probability"],
                absurdity=absurdity_val
            )
        )

    return results


def calculate_uselessness_score(results: List[SearchResult], recommendation: str) -> int:
    """
    Deterministically computes a Uselessness Score (70% - 99%) based on:
    - Average absurdity of explanations
    - Escalation gradient from Tier 1 to Tier 5
    - Recommendation confidence and length
    """
    if not results:
        return 88

    avg_absurdity = sum(r.absurdity for r in results) / len(results)
    escalation_spread = results[-1].absurdity - results[0].absurdity
    rec_length_mod = (len(recommendation) % 11) / 100.0

    raw_score = (avg_absurdity * 60) + (escalation_spread * 25) + (rec_length_mod * 15)
    # Scale comfortably into the 78% - 98% "Peak Futility" zone
    score = int(round(72 + (raw_score * 0.26)))
    return max(70, min(99, score))


def generate_offline_fallback(query: str) -> Dict[str, Any]:
    """
    Zero-failure, context-sensitive fallback generator for demonstrations
    when API credentials are not provided or remote services are unavailable.
    """
    q_lower = query.lower()

    if any(k in q_lower for k in ["'k'", " k ", " k", "text", "message", "reply", "ghost", "left on read", "say okay", "okay", "ok"]):
        results = [
            {"text": "They were rushing into an elevator or their battery dropped to 1%.", "probability": 42, "absurdity": 0.12},
            {"text": "They found 'ok' too formal and wanted to convey breezy, unbothered minimalism.", "probability": 28, "absurdity": 0.34},
            {"text": "They typed a thoughtful 3-paragraph reply, panicked over vulnerability, deleted it, and sent 'k'.", "probability": 18, "absurdity": 0.59},
            {"text": "Their phone was intercepted by foreign intelligence operatives trained only in single-consonant reconnaissance.", "probability": 8, "absurdity": 0.82},
            {"text": "You have slipped into a parallel universe where vowels have been banned by an authoritarian algorithm.", "probability": 4, "absurdity": 0.98},
        ]
        rec = "DO NOTHING. (Or draft a 14-page handwritten letter via carrier pigeon requesting punctuation clarification)."
        conf = "99.4% Suspiciously High"

    elif any(k in q_lower for k in ["boss", "manager", "work", "email", "slack", "fired", "meeting", "period"]):
        results = [
            {"text": "They use standard punctuation because they belong to an older generation that fears emojis.", "probability": 44, "absurdity": 0.15},
            {"text": "They were typing between back-to-back syncs and didn't register the passive-aggressive tone.", "probability": 26, "absurdity": 0.36},
            {"text": "They noticed you spent 17 minutes browsing mechanical keyboard forums on the corporate network.", "probability": 16, "absurdity": 0.62},
            {"text": "HR has already synthesized an automated replacement clone that requires 30% less iced coffee.", "probability": 10, "absurdity": 0.84},
            {"text": "The period at the end of the sentence is an encoded GPS beacon summoning auditors to repossess your swivel chair.", "probability": 4, "absurdity": 0.96},
        ]
        rec = "Preemptively submit a resignation letter in Morse code, then hide under your desk in high-visibility apparel."
        conf = "104% Workplace Anxiety"

    elif any(k in q_lower for k in ["cat", "dog", "pet", "stare", "staring", "animal", "look"]):
        results = [
            {"text": "A microscopic gnat was drifting 2 inches past your left ear.", "probability": 45, "absurdity": 0.10},
            {"text": "They are evaluating whether your current emotional state warrants a slice of cheddar cheese.", "probability": 27, "absurdity": 0.32},
            {"text": "They have detected an ancestral spirit standing behind you giving unsolicited fashion critiques.", "probability": 16, "absurdity": 0.60},
            {"text": "They are transmitting daily telepathic surveillance dossiers to the interstellar mothership.", "probability": 8, "absurdity": 0.83},
            {"text": "You are actually the pet in this dimensional simulation, and their quarterly performance review of you is due at 5 PM.", "probability": 4, "absurdity": 0.97},
        ]
        rec = "Bow respectfully, sacrifice a cube of mild cheddar, and avoid direct eye contact for 48 hours."
        conf = "97.8% Interspecies Certainty"

    else:
        words = re.findall(r'\b\w{4,}\b', query)
        kw1 = words[0].capitalize() if words else "The Situation"
        kw2 = words[1].capitalize() if len(words) > 1 else "The Universe"

        results = [
            {"text": f"The most boring truth applies: circumstances aligned by sheer random coincidence regarding {kw1.lower()}.", "probability": 41, "absurdity": 0.12},
            {"text": f"Someone observed a micro-hesitation regarding {kw1.lower()} and is cautiously hedging.", "probability": 27, "absurdity": 0.35},
            {"text": f"Both parties entered a recursive loop of mutual second-guessing regarding {kw2.lower()}.", "probability": 18, "absurdity": 0.58},
            {"text": f"A secretive shadow council decided today was the optimal date to stress-test your coping mechanisms.", "probability": 9, "absurdity": 0.82},
            {"text": f"A localized spacetime anomaly swapped your timeline with one where {kw1.lower()} dictates quantum physics.", "probability": 5, "absurdity": 0.96},
        ]
        rec = f"Burn all digital receipts, delete system cache, and speak solely in ancient riddles regarding {kw1.lower()}."
        conf = "99.1% Unearned Certainty"

    return {
        "results": results,
        "recommendation": rec,
        "confidence": conf,
        "engine_used": "Autonomous Deduction Matrix"
    }
