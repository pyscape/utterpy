Python bindings for utter, the zero-dependency pure-Rust streaming speech decoder for Vosk (Kaldi nnet3) models. Drop-in for the vosk wheel's API: feed 16 kHz audio, read the partial after every block, the live n-best from the beam, word times, endpoints. No C toolchain, no Docker, no cloud.

## Use

```python
import json, utterpy

model = utterpy.Model("vosk-model-small-en-us-0.15")
rec = utterpy.KaldiRecognizer(model, 16000, json.dumps(["yes", "no", "stop"]))
rec.SetWords(True)
rec.SetPartialWords(True)
rec.SetPartialAlternatives(3)

for block in blocks_of_16k_mono_int16_pcm:      # bytes, 40 ms works well
    if rec.AcceptWaveform(block):                # an endpoint fired
        print(json.loads(rec.Result()))          # {"result": [...], "text": ...}
    else:
        print(json.loads(rec.PartialResult()))   # {"partial": ..., "partial_alternatives": [...], "partial_result": [...]}
print(json.loads(rec.FinalResult()))
```

The method names are vosk's, and the JSON keeps vosk's layout. On top of
it: `partial_alternatives` (distinct readings alive in the beam, with
`confidence` as the negated cost), `partial_result` entries with
`start_sample`, `end_sample`, `energy_dbfs` and `stable_ms`, `[sil]` as
the reading when the best path carries no word and sits on silence and
`[speech]` when it has entered a word's phones, `endpoint` on a final
naming the rule that closed it and `stable_ms` on each final word for
the hold it had in the partial, and an optional
`unknown_cost` argument to the recognizer that admits the model's
unknown-word symbol. `DecodedSample()` gives the position, in samples fed,
of the last decoded frame.

## Build

```
python -m venv .venv && . .venv/bin/activate
pip install maturin
maturin develop --release        # into the venv
maturin build --release          # a wheel under target/wheels
```

The core is fetched from the pinned revision of
github.com/pyscape/utter. To build against a checkout beside this one
instead, put this in `.cargo/config.toml` (ignored by git):

```toml
[patch."https://github.com/pyscape/utter.git"]
utter = { path = "../utter" }
```

The wheel has no runtime dependencies.

## Release

GitHub Actions builds wheels for Linux x86_64 and aarch64 (manylinux
2_28), Windows x64, and macOS x86_64 and arm64 on every push, and on a
`v*` tag attaches them to a GitHub release and publishes to PyPI through
trusted publishing. Publishing works once the PyPI project names this
repository's `wheels.yml` workflow and the `pypi` environment as a
trusted publisher; no token lives in the repository.
