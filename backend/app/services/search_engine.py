import re
from typing import Any, Dict, List
from app.schemas.search import SearchResult

TIER_METADATA = [
    {"tier": 1, "title": "Mundane Reality", "default_absurdity": 0.12},
    {"tier": 2, "title": "Mild Paranoia", "default_absurdity": 0.35},
    {"tier": 3, "title": "The Overthought Spiral", "default_absurdity": 0.58},
    {"tier": 4, "title": "Suspiciously Specific Plot", "default_absurdity": 0.81},
    {"tier": 5, "title": "Completely Unhinged", "default_absurdity": 0.96},
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
            {"text": "They were holding two lukewarm coffees and a grocery bag with a snapped handle, typed with only their chin, and immediately forgot you exist.", "probability": 42, "absurdity": 0.12},
            {"text": "They drafted a warm 3-sentence reply, noticed it contained an exclamation mark, felt sickeningly vulnerable, deleted everything, and sent a single monosyllable to re-establish emotional dominance.", "probability": 28, "absurdity": 0.35},
            {"text": "They read a LinkedIn article in 2017 about 'executive presence' and have spent the last seven years slowly incinerating their personal relationships one stone-cold reply at a time.", "probability": 18, "absurdity": 0.59},
            {"text": "They are auditioning for the role of a disillusioned Swedish detective in a bleak Nordic noir series and are method-acting emotional detachment across all incoming text messages.", "probability": 8, "absurdity": 0.82},
            {"text": "Their phone was momentarily commandeered by an eccentric raccoon that lives behind their garage and only knows how to accept invitations to social gatherings it has no intention of attending.", "probability": 4, "absurdity": 0.97},
        ]
        rec = "DO NOTHING. In fact, do less than nothing. Leave your phone face-down on a wooden coaster, stare blankly at a floor lamp for 42 minutes, and let the awkwardness ripen into a fine vintage."
        conf = "104% Unearned Certainty"

    elif any(k in q_lower for k in ["boss", "manager", "work", "email", "slack", "fired", "meeting", "period"]):
        results = [
            {"text": "They were typing on their phone while navigating a revolving door and their thumbs simply gave up midway through typing a polite pleasantry.", "probability": 44, "absurdity": 0.14},
            {"text": "They use standard punctuation because they belong to a demographic that perceives exclamation points as legally binding promises of eternal friendship.", "probability": 26, "absurdity": 0.36},
            {"text": "They spent 11 minutes debating between 'Best,' 'Warm regards,' and 'Thanks,', panicked over whether 'Best' sounded too sensual, and settled on an aggressive full stop out of pure executive fear.", "probability": 16, "absurdity": 0.62},
            {"text": "They noticed you spent 23 minutes reorganizing color-coded tabs on a spreadsheet that hasn't been opened by another human being since November 2021, and this is their silent retaliation.", "probability": 10, "absurdity": 0.84},
            {"text": "HR has calculated that enthusiastic workplace correspondence consumes 14% too much corporate bandwidth, so management is now legally mandated to communicate like 19th-century Victorian undertakers.", "probability": 4, "absurdity": 0.96},
        ]
        rec = "Reply 'Understood.' with exactly two periods at the end. That is an illegal quantity of punctuation. It establishes chaotic neutral energy and buys you four business days of terrified silence."
        conf = "98.7% Corporate Neurosis"

    elif any(k in q_lower for k in ["cat", "dog", "pet", "stare", "staring", "animal", "look"]):
        results = [
            {"text": "There is a microscopic piece of lint floating four inches in front of your forehead that you are too biologically inferior to perceive.", "probability": 45, "absurdity": 0.10},
            {"text": "They are actively evaluating your weekly performance as a roommate and have noted three instances where you sneezed without apologizing to the room.", "probability": 27, "absurdity": 0.33},
            {"text": "They are wondering why you have been wearing the exact same pair of fleece sweatpants for three consecutive days and whether this indicates a collapse in pack leadership.", "probability": 16, "absurdity": 0.60},
            {"text": "They are convinced you are an unusually large, hairless cat with severe learning disabilities who somehow mastered the can opener, and they are silently pitying your condition.", "probability": 8, "absurdity": 0.83},
            {"text": "They are conducting a high-level telepathic treaty with the refrigerator compressor, offering your leftover pasta in exchange for not howling at 4:15 AM.", "probability": 4, "absurdity": 0.97},
        ]
        rec = "Do not blink. Do not apologize. Slowly slide a single slice of mild cheddar across the floor and walk backward into another room while softly humming a national anthem."
        conf = "99.8% Interspecies Judgment"

    else:
        words = re.findall(r'\b\w{4,}\b', query)
        kw1 = words[0].capitalize() if words else "The Situation"
        kw2 = words[1].capitalize() if len(words) > 1 else "The Universe"

        results = [
            {"text": f"The most boring truth applies: circumstances regarding {kw1.lower()} aligned by mundane coincidence, but your brain chose to interpret it as a targeted personal insult.", "probability": 41, "absurdity": 0.12},
            {"text": f"Someone involved with {kw1.lower()} drafted an honest reply, realized it required 4% more emotional effort than they possessed, and decided to let awkward silence do the heavy lifting.", "probability": 27, "absurdity": 0.35},
            {"text": f"Both parties entered a recursive loop of polite second-guessing regarding {kw2.lower()}, each waiting for the other to break protocol so they can claim moral high ground.", "probability": 18, "absurdity": 0.58},
            {"text": f"An intensely specific municipal bylaw from 1984 technically prohibits any straightforward resolution to {kw1.lower()}, and someone is quietly enforcing it out of sheer spite.", "probability": 9, "absurdity": 0.82},
            {"text": f"A localized committee of mildly inconvenienced acquaintances concluded that leaving {kw1.lower()} unresolved was 37% more entertaining than giving you closure.", "probability": 5, "absurdity": 0.96},
        ]
        rec = f"DO NOTHING. Mention '{kw1.lower()}' to a passing pigeon, delete your browser cache, and pretend you have moved to an undisclosed coastal village."
        conf = "102% Clinically Overthought"

    return {
        "results": results,
        "recommendation": rec,
        "confidence": conf,
        "engine_used": "Autonomous Deduction Matrix"
    }
