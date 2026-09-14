"""Decode the bundled clips against a stock Vosk model and check the vosk-shaped output."""

from __future__ import annotations

import json
import os
import random
import struct
import wave
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
import utterpy

DATA = Path(__file__).resolve().parent / "data"
GRAMMAR = json.dumps(["yes", "no", "stop"])
BLOCK = 1280
WORDLESS = ("", "[sil]", "[speech]")
SECOND_OF_SILENCE = struct.pack("<16000h", *([0] * 16000))


def model_path() -> Path | None:
    named = os.environ.get("UTTER_TEST_MODEL")
    if named:
        return Path(named)
    models = Path(__file__).resolve().parent.parent / "models"
    if models.is_dir():
        for entry in sorted(models.iterdir()):
            if (entry / "am").is_dir():
                return entry
    return None


@pytest.fixture(scope="module")
def model() -> utterpy.Model:
    path = model_path()
    if path is None:
        pytest.skip("no model: set UTTER_TEST_MODEL or unpack one under models/")
    return utterpy.Model(str(path))


def recognizer(model: utterpy.Model) -> utterpy.KaldiRecognizer:
    rec = utterpy.KaldiRecognizer(model, 16000, GRAMMAR)
    rec.SetWords(True)
    rec.SetPartialWords(True)
    rec.SetPartialAlternatives(3)
    return rec


def clip(name: str) -> bytes:
    with wave.open(str(DATA / f"{name}.wav"), "rb") as w:
        assert w.getframerate() == 16000 and w.getnchannels() == 1
        return w.readframes(w.getnframes())


def blocks(pcm: bytes) -> Iterator[bytes]:
    for start in range(0, len(pcm), BLOCK):
        yield pcm[start : start + BLOCK]


def stream(rec: utterpy.KaldiRecognizer, pcm: bytes) -> list[dict[str, Any]]:
    """Every partial and final in order, as decoded dicts."""
    out: list[dict[str, Any]] = []
    for block in blocks(pcm):
        fired = rec.AcceptWaveform(block)
        text = rec.Result() if fired else rec.PartialResult()
        out.append(json.loads(text))
    out.append(json.loads(rec.FinalResult()))
    return out


def worded_finals(readings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [r for r in readings if "text" in r and r["text"] not in WORDLESS]


@pytest.mark.parametrize("word", ["yes", "no", "stop"])
def test_final_reads_the_word(model: utterpy.Model, word: str) -> None:
    rec = recognizer(model)
    (final,) = worded_finals(stream(rec, clip(word) + SECOND_OF_SILENCE))
    assert final["text"] == word
    (entry,) = final["result"]
    assert entry["word"] == word
    assert entry["stable_ms"] > 0
    assert 0 <= entry["start"] < entry["end"] <= 2.0
    assert isinstance(entry["energy_dbfs"], float) and entry["energy_dbfs"] < 0


def test_word_shows_in_a_partial_before_the_final(model: utterpy.Model) -> None:
    rec = recognizer(model)
    partials = [r for r in stream(rec, clip("yes") + SECOND_OF_SILENCE) if "partial" in r]
    assert any(r["partial"] == "yes" for r in partials)
    shown = next(r for r in partials if r["partial"] == "yes")
    (entry,) = [e for e in shown["partial_result"] if e["word"] == "yes"]
    assert entry["end_sample"] > entry["start_sample"]
    assert all("confidence" in alt for alt in shown["partial_alternatives"])


def test_silence_is_a_wordless_reading(model: utterpy.Model) -> None:
    rec = recognizer(model)
    readings = stream(rec, SECOND_OF_SILENCE * 2)
    assert worded_finals(readings) == []
    assert all(r.get("partial", r.get("text")) in WORDLESS for r in readings)


def test_endpoint_bound_fires_and_names_itself(model: utterpy.Model) -> None:
    rec = recognizer(model)
    rec.SetEndpointBound(300.0, 8.0)
    (final,) = worded_finals(stream(rec, clip("stop") + SECOND_OF_SILENCE * 2))
    assert final["text"] == "stop"
    assert isinstance(final["endpoint"], str)


def test_digital_silence_has_no_energy_and_no_floor(model: utterpy.Model) -> None:
    rec = recognizer(model)
    readings = stream(rec, SECOND_OF_SILENCE * 2)
    assert all("floor_dbfs" not in r for r in readings)
    entries = [e for r in readings for e in r.get("partial_result", r.get("result", []))]
    assert entries and all(e["energy_dbfs"] is None for e in entries)


def test_floor_margin_does_not_cut_a_word_short(model: utterpy.Model) -> None:
    # Digital zeros have no floor to measure against, so the room is low white noise. The
    # wordless span right after the word is shorter than the bound, so the margin must not read
    # it as silence: utter 0.0.3 did, closing the word early, and 0.0.4 does not.
    rng = random.Random(1)
    noise = struct.pack("<48000h", *[rng.randint(-30, 30) for _ in range(48000)])

    def closing(margin: float | None) -> tuple[str, int]:
        rec = recognizer(model)
        rec.SetEndpointBound(300.0, 8.0)
        rec.SetEndpointFloorMargin(margin)
        readings = stream(rec, clip("stop") + noise)
        (final,) = worded_finals(readings)
        assert final["text"] == "stop"
        return final["endpoint"], readings.index(final)

    assert closing(6.0) == closing(None)


def test_decoded_sample_tracks_the_audio_fed(model: utterpy.Model) -> None:
    rec = recognizer(model)
    pcm = clip("no")
    stream(rec, pcm)
    assert 0 < rec.DecodedSample() <= len(pcm) // 2


def test_reset_clears_the_reading(model: utterpy.Model) -> None:
    rec = recognizer(model)
    stream(rec, clip("yes"))
    rec.Reset()
    assert json.loads(rec.PartialResult()).get("partial", "") in WORDLESS
