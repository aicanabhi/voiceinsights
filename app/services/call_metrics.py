"""Call metrics derived from speaker segments.

Pure arithmetic over data already stored in transcript_segments -- no provider
or LLM call involved, so these are free and work retroactively on calls that
were transcribed before this existed.

Speakers are NOT guessed as "agent" / "customer": diarization only numbers
them by who speaks first. Per-speaker figures are reported by index and the
caller decides the labels.
"""

from typing import Any, Optional


# Below this, the ASR was unsure -- usually poor audio, accent, or crosstalk.
LOW_CONFIDENCE_THRESHOLD = 0.90

# Gaps shorter than this are natural conversational rhythm, not dead air.
DEAD_AIR_SECONDS = 2.0


def _round(value: Optional[float], places: int = 2) -> Optional[float]:
    return None if value is None else round(value, places)


def compute_call_metrics(segments: list[Any]) -> Optional[dict]:
    """Returns None when there is nothing to measure (e.g. a provider that
    does not diarize, so no segments were stored)."""

    rows = []

    for s in segments or []:

        start = getattr(s, "start_time", None)
        end = getattr(s, "end_time", None)

        if start is None or end is None:
            continue

        rows.append({
            "speaker": getattr(s, "speaker", 0),
            "text": getattr(s, "text", "") or "",
            "start": float(start),
            "end": max(float(end), float(start)),
            "confidence": getattr(s, "confidence", None),
        })

    if not rows:
        return None

    rows.sort(key=lambda r: (r["start"], r["end"]))

    duration = max(r["end"] for r in rows) - min(r["start"] for r in rows)

    # ---- per speaker -------------------------------------------------
    per_speaker: dict[int, dict] = {}

    for r in rows:

        stats = per_speaker.setdefault(
            r["speaker"],
            {"talk_seconds": 0.0, "words": 0, "longest_turn": 0.0},
        )

        length = r["end"] - r["start"]

        stats["talk_seconds"] += length
        stats["words"] += len(r["text"].split())
        stats["longest_turn"] = max(stats["longest_turn"], length)

    total_speech = sum(s["talk_seconds"] for s in per_speaker.values())

    speakers = []

    for speaker, stats in sorted(per_speaker.items()):

        talk = stats["talk_seconds"]

        speakers.append({
            "speaker": speaker,
            "talk_seconds": _round(talk),
            "talk_percent": _round(
                (talk / total_speech * 100) if total_speech else None
            ),
            "words": stats["words"],
            "words_per_minute": _round(
                (stats["words"] / (talk / 60)) if talk > 0 else None
            ),
            "longest_turn_seconds": _round(stats["longest_turn"]),
        })

    # ---- gaps, overlaps, turns --------------------------------------
    silences: list[tuple[float, float]] = []
    latencies: list[float] = []
    interruptions = []
    turns = 0

    for prev, nxt in zip(rows, rows[1:]):

        gap = nxt["start"] - prev["end"]
        speaker_changed = prev["speaker"] != nxt["speaker"]

        if speaker_changed:
            turns += 1

        if gap < 0:
            # next speaker started before the previous one finished
            if speaker_changed:
                interruptions.append({
                    "at_seconds": _round(nxt["start"]),
                    "by_speaker": nxt["speaker"],
                    "overlap_seconds": _round(-gap),
                })
            continue

        if gap >= DEAD_AIR_SECONDS:
            silences.append((gap, prev["end"]))

        if speaker_changed:
            latencies.append(gap)

    longest_silence = max(silences, default=None)

    talk_ratio = None

    if len(speakers) == 2:
        a, b = speakers[0]["talk_seconds"], speakers[1]["talk_seconds"]
        talk_ratio = _round(a / b) if b else None

    confidences = [
        r["confidence"] for r in rows if r["confidence"] is not None
    ]

    return {
        "duration_seconds": _round(duration),
        "speech_seconds": _round(total_speech),
        "silence_seconds": _round(sum(g for g, _ in silences)),
        "longest_silence_seconds": _round(
            longest_silence[0] if longest_silence else 0.0
        ),
        "longest_silence_at": _round(
            longest_silence[1] if longest_silence else None
        ),

        "segments": len(rows),
        "turns": turns,

        "interruptions": len(interruptions),
        "interruption_details": interruptions[:10],

        "avg_response_latency_seconds": _round(
            sum(latencies) / len(latencies) if latencies else None
        ),
        "max_response_latency_seconds": _round(
            max(latencies) if latencies else None
        ),

        "speakers": speakers,
        "talk_ratio": talk_ratio,

        # None (not 0) when the provider gave no confidence at all
        "low_confidence_segments": (
            sum(1 for c in confidences if c < LOW_CONFIDENCE_THRESHOLD)
            if confidences else None
        ),
        "average_confidence": _round(
            sum(confidences) / len(confidences) if confidences else None
        ),
    }
