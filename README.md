# utterpy

[![PyPI](https://img.shields.io/pypi/v/utterpy)](https://pypi.org/project/utterpy/)
[![Python](https://img.shields.io/pypi/pyversions/utterpy)](https://pypi.org/project/utterpy/)
[![Wheels](https://github.com/pyscape/utterpy/actions/workflows/wheels.yml/badge.svg)](https://github.com/pyscape/utterpy/actions/workflows/wheels.yml)
[![CodeQL](https://github.com/pyscape/utterpy/actions/workflows/codeql.yml/badge.svg)](https://github.com/pyscape/utterpy/actions/workflows/codeql.yml)
[![cargo-deny](https://github.com/pyscape/utterpy/actions/workflows/deny.yml/badge.svg)](https://github.com/pyscape/utterpy/actions/workflows/deny.yml)
[![Scorecard](https://api.scorecard.dev/projects/github.com/pyscape/utterpy/badge)](https://scorecard.dev/viewer/?uri=github.com/pyscape/utterpy)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Python bindings for utter, the zero-dependency pure-Rust streaming
speech decoder for Vosk (Kaldi nnet3) models. Drop-in for the vosk
wheel's API: feed 16 kHz audio, read the partial after every block, the
live n-best from the beam, word times, endpoints. No C toolchain, no
Docker, no cloud.

## Why

The vosk wheel is a C++ wrapper around Kaldi: no Windows build without
Docker, and one more field out of the decoder means a fork. utter
reimplements what a Vosk model needs, in Rust, from a stock model
directory, and is checked block for block against the wheel. Figures
are from the [benchmark pages](https://github.com/pyscape/utter/blob/main/docs/benchmarks/README.md),
paired against the wheel on identical audio.

- **Silence is in the stream.** Every partial says `[sil]` or
  `[speech]` when it carries no word; every final names the rule that
  closed it; every word carries its energy against the room floor and
  how long it held. The wheel gives a bare string, so a phantom over
  mic hiss and a spoken word look the same
  ([TD-10](https://github.com/pyscape/utter/blob/main/docs/td/0010-a-wordless-reading-says-whether-a-word-has-begun.md),
  [TD-11](https://github.com/pyscape/utter/blob/main/docs/td/0011-a-final-says-what-closed-it-and-how-long-its-words-held.md)).
- **Phantoms are tellable, not fewer.** On wordless audio both engines
  read alike: no rank-0 word on cold silence under 92 entries, 0.56 per
  minute after speech. Here each carries `stable_ms` and `energy_dbfs`,
  so a stale word is told from a fresh one, and the partial stream is
  as steady as the wheel's: first word later revised on 12.4% of clips
  against 12.3% ([speech-commands.md](https://github.com/pyscape/utter/blob/main/docs/benchmarks/speech-commands.md)).
- **A host endpoint bound.** A final after N ms of trailing silence,
  vetoed while a rival is within a margin. Median finish 866 to 660 ms
  on built streams, same finishes called, no word lost or split
  ([partial-states.md](https://github.com/pyscape/utter/blob/main/docs/benchmarks/partial-states.md),
  [TD-8](https://github.com/pyscape/utter/blob/main/docs/td/0008-silence-is-the-hosts-gate.md)).
- **Distinct rivals with their motion** on every partial, where the
  wheel's alternatives repeat readings
  ([TD-9](https://github.com/pyscape/utter/blob/main/docs/td/0009-readings-carry-their-relation-and-their-leads-motion.md)).
- **Parity, not a gain, on hearing.** 91.79% against 91.49% on 11,005
  clips, finals identical on 99.2%, word times to the frame, same 40 ms
  first appearance, less compute
  ([word-times.md](https://github.com/pyscape/utter/blob/main/docs/benchmarks/word-times.md)).
- **Pure Rust, typed.** No C toolchain, no Docker, no cloud. Wheels for
  Linux, macOS and Windows, one abi3 build from Python 3.9, with a stub
  and py.typed checked by stubtest.

| Speech Commands v2, 11,005 clips | Vosk 0.3.45 | utter |
|---|---|---|
| Accuracy, full grammar | 91.49% | 91.79% |
| First word shown after the clip ends, p50 / p90 | 40 / 250 ms | 40 / 250 ms |
| First word shown later revised | 12.3% | 12.4% |
| Real-time factor, decode only | 0.0168 | 0.0143 |

Pre-alpha; the decoder still moves between revisions.

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

## Configure

The calls are the wheel's, so switching is the import. The setup the
pages measure:

```python
rec = utterpy.KaldiRecognizer(model, 16000, json.dumps(grammar))
rec.SetWords(True)              # word times, energy_dbfs, stable_ms on finals
rec.SetPartialWords(True)       # word entries on partials, with [sil]/[speech]
rec.SetPartialAlternatives(4)   # four distinct readings per partial
rec.SetMaxAlternatives(4)       # n-best finals
rec.SetEndpointBound(300, 8)    # host bound with veto; (ms, 0) bare, (0) off
```

Feed 40 ms blocks, 1280 bytes at 16 kHz mono int16. Two clocks: a
word shows in the partial 40 ms after it ends, the block size, for
both engines; the final arrives 866 ms after under the model's rules
and 660 ms with the bound. Compute is not the wait, at 0.04 ms per
block. The trailing `[sil]` entry shows in the partial before the
endpoint fires, so a host can act on a settled partial plus visible
silence.

- Expose the bound as one host setting with an off spelling, and
  measure off against on on your own replays before retuning it.
- Model conf carries over: `frames_per_chunk` and
  `min-trailing-silence` tuned for the wheel keep their effect.
- `unknown_cost` does not fight phantoms; the page measured no change
  in rank-0 words. The fields and the bound are the levers.
- Grammar size sets the stale-partial rate after speech: about 0.6 per
  minute at 92 entries, 3 at 150.
- Keep a trace of raw partial and final payloads. `SetLogLevel(-1)`
  silences the runtime as with the wheel.

## Silence

Host rules that have held up, each keyed off one field:

- `[sil]` and `[speech]` are no word: never dispatched, ranked or
  shown. When rank 0 is wordless, offer nothing; the rivals beneath
  it on floor audio are short grammar words at low confidence.
- Drop a final word with `"endpoint": "rule5"` and `"stable_ms": 0`.
  That is Kaldi's 20 s length cap naming the cheapest word over
  silence, every 21 s on mic hiss, on the wheel too. When the drop
  empties the final, still close the utterance, or the phantom returns
  as a partial. Do not widen this to `rule2`: a never-shown word there
  can be a real rescored reading.
- Keep the bound on with the veto. Shorter bounds are fine with it
  and cut phrases into pieces without it.
- Gate on `energy_dbfs` at least 8 dB above `floor_dbfs` only after
  scoring it on your replays: it removes about half the worded finals
  on room silence and costs real words near the floor.

## Build

```sh
python -m venv .venv && . .venv/bin/activate
pip install maturin
maturin develop --release        # into the venv
maturin build --release          # a wheel under target/wheels
```

The core is the utter crate from crates.io at the version Cargo.toml
names. To build against a checkout beside this one instead, put this
in `.cargo/config.toml` (ignored by git):

```toml
[patch.crates-io]
utter = { path = "../utter" }
```

The wheel has no runtime dependencies.

The wheel carries py.typed and a stub for the module, so a type checker
sees the API without a separate stubs package.

## Release

GitHub Actions builds wheels for Linux x86_64 and aarch64 (manylinux
2_28 and musllinux 1.2), Windows x64, and macOS x86_64 and arm64 on
every push, runs the tests on Python 3.9 to 3.14, and on a
`v*` tag attaches them to a GitHub release and publishes to PyPI through
trusted publishing. Publishing works once the PyPI project names this
repository's `wheels.yml` workflow and the `pypi` environment as a
trusted publisher; no token lives in the repository.
