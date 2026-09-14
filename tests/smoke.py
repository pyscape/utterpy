"""Import the extension and check the vosk-shaped surface, with a model when one is on hand."""

import json
import os
import struct
import wave
from pathlib import Path
from typing import Optional

import utterpy

assert utterpy.Recognizer is utterpy.KaldiRecognizer
for name in [
    "SetWords",
    "SetPartialWords",
    "SetPartialAlternatives",
    "SetMaxAlternatives",
    "SetEndpointBound",
    "SetEndpointFloorMargin",
    "AcceptWaveform",
    "PartialResult",
    "Result",
    "FinalResult",
    "Reset",
    "DecodedSample",
]:
    assert hasattr(utterpy.KaldiRecognizer, name), name
assert hasattr(utterpy.Model, "FindWord")
utterpy.SetLogLevel(-1)
try:
    utterpy.Model("/nonexistent")
except RuntimeError:
    pass
else:
    raise SystemExit("opening a missing model should fail")


def model_path() -> Optional[Path]:
    named = os.environ.get("UTTER_TEST_MODEL")
    if named:
        return Path(named)
    models = Path(__file__).resolve().parent.parent / "models"
    if models.is_dir():
        for entry in sorted(models.iterdir()):
            if (entry / "am").is_dir():
                return entry
    return None


def read_pcm(path: Path) -> bytes:
    with wave.open(str(path), "rb") as w:
        return w.readframes(w.getnframes())


def decode(path: Path) -> None:
    model = utterpy.Model(str(path))
    assert model.FindWord("<s>") >= -1
    rec = utterpy.KaldiRecognizer(model, 16000, json.dumps(["yes", "no", "stop"]))
    rec.SetWords(True)
    rec.SetPartialWords(True)
    rec.SetPartialAlternatives(3)
    rec.SetMaxAlternatives(0)
    rec.SetEndpointBound(500.0, None)
    clip = next(iter(sorted(path.parent.glob("*.wav"))), None)
    pcm = read_pcm(clip) if clip is not None else struct.pack("<800h", *([0] * 800))
    block = 1280
    for start in range(0, len(pcm) - len(pcm) % 2, block):
        chunk = pcm[start : start + block]
        fired: bool = rec.AcceptWaveform(chunk)
        text = rec.Result() if fired else rec.PartialResult()
        assert isinstance(json.loads(text), dict)
    assert isinstance(rec.DecodedSample(), int)
    assert isinstance(json.loads(rec.FinalResult()), dict)
    rec.Reset()


found = model_path()
if found is not None:
    decode(found)
    print("utterpy", utterpy.__version__, "decoded with", found.name)
else:
    print("utterpy", utterpy.__version__, "surface ok; no model, set UTTER_TEST_MODEL to decode")
