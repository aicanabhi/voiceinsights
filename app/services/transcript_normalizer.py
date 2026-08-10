"""Canonical shape for speaker segments.

Each provider returns something different -- Deepgram gives utterances with a
confidence, ElevenLabs gives one entry per word, Cartesia gives nothing. Every
provider service funnels its output through here so the rest of the app (DB
rows, call metrics, the transcript UI) only ever sees one shape:

    {"speaker": int, "text": str, "start": float, "end": float,
     "confidence": float | None}
"""

import re
from typing import Any, Iterable, Optional


# A pause longer than this splits one speaker's words into separate utterances,
# so a whole monologue does not collapse into a single unreadable block.
UTTERANCE_GAP_SECONDS = 1.0


class SpeakerMap:
    """Maps whatever a provider calls a speaker ("speaker_0", 3, None) onto
    stable 0-based ints, in the order they first speak."""

    def __init__(self):
        self._seen: dict[Any, int] = {}

    def to_index(self, raw: Any) -> int:

        key = "?" if raw is None else raw

        if key not in self._seen:
            self._seen[key] = len(self._seen)

        return self._seen[key]


def _clean(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    # joining words with spaces leaves " ," / " ." behind
    return re.sub(r"\s+([,.!?;:])", r"\1", text)


def _as_float(value: Any) -> Optional[float]:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def normalize_utterances(raw_segments: Iterable[dict]) -> list[dict]:
    """For providers that already return utterance-level segments."""

    speakers = SpeakerMap()
    out = []

    for seg in raw_segments:

        text = _clean(str(seg.get("text") or ""))
        start = _as_float(seg.get("start"))
        end = _as_float(seg.get("end"))

        if not text or start is None or end is None:
            continue

        out.append({
            "speaker": speakers.to_index(seg.get("speaker")),
            "text": text,
            "start": start,
            "end": max(end, start),
            "confidence": _as_float(seg.get("confidence")),
        })

    return out


def words_to_utterances(words: Iterable[dict]) -> list[dict]:
    """For providers that return one entry per word (ElevenLabs).

    Consecutive words from the same speaker are merged until the speaker
    changes or a pause longer than UTTERANCE_GAP_SECONDS appears.
    """

    speakers = SpeakerMap()
    out: list[dict] = []
    current: Optional[dict] = None

    for word in words:

        # ElevenLabs interleaves spacing/audio-event entries between words
        if word.get("type") not in (None, "word"):
            continue

        text = str(word.get("text") or "")

        if not text.strip():
            continue

        start = _as_float(word.get("start"))
        end = _as_float(word.get("end"))

        if start is None or end is None:
            continue

        speaker = speakers.to_index(
            word.get("speaker_id", word.get("speaker"))
        )

        confidence = _as_float(
            word.get("confidence", word.get("logprob"))
        )

        same_turn = (
            current is not None
            and current["speaker"] == speaker
            and start - current["end"] <= UTTERANCE_GAP_SECONDS
        )

        if same_turn:
            current["text"] += " " + text.strip()
            current["end"] = max(end, current["end"])
            current["_confidences"].append(confidence)
            continue

        if current is not None:
            out.append(_finish(current))

        current = {
            "speaker": speaker,
            "text": text.strip(),
            "start": start,
            "end": end,
            "_confidences": [confidence],
        }

    if current is not None:
        out.append(_finish(current))

    return out


def _finish(pending: dict) -> dict:

    values = [c for c in pending.pop("_confidences") if c is not None]

    return {
        "speaker": pending["speaker"],
        "text": _clean(pending["text"]),
        "start": pending["start"],
        "end": max(pending["end"], pending["start"]),
        "confidence": (sum(values) / len(values)) if values else None,
    }
