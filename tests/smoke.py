"""Import the extension and check the vosk-shaped surface without a model."""
import utterpy

assert utterpy.Recognizer is utterpy.KaldiRecognizer
for name in ["SetWords", "SetPartialWords", "SetPartialAlternatives", "SetMaxAlternatives",
             "AcceptWaveform", "PartialResult", "Result", "FinalResult", "Reset", "DecodedSample"]:
    assert hasattr(utterpy.KaldiRecognizer, name), name
assert hasattr(utterpy.Model, "FindWord")
utterpy.SetLogLevel(-1)
try:
    utterpy.Model("/nonexistent")
except RuntimeError:
    pass
else:
    raise SystemExit("opening a missing model should fail")
print("utterpy", utterpy.__version__, "surface ok")
