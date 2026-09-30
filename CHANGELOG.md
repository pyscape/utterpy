# Changelog

Notable changes to the wheel, newest first. The project follows semantic
versioning; release dates are recorded by the git tags and the GitHub
releases.

## 0.0.6

- TitaNet-small speaker evidence, from utter 0.0.6: `SpkModel(path)`
  also opens a TitaNet-small directory converted by utter's
  scripts/titanet_convert.py, and `dim()` is 192. Set on a recognizer,
  it embeds each word's span on a thread of the recognizer's own, and
  the word's entry carries `spk`, `spk_frames`, `spk_start` and
  `spk_end`; partials and finals carry no top-level evidence. Needs
  audio at 16 kHz or faster. One word clears a gate at 1% false accept
  81.2% of the time, against 41.6% with the x-vector, which stays for
  audio below 16 kHz.
- `SpkModel.embed(data, sample_rate=16000)`: the embedding of a span of
  float32 samples without a recognizer, with the GIL released.
- The acoustic model's certainty and the sound outside words, on every
  partial and final, always on: `certainty_words`,
  `certainty_outside`, `words_frames`, `outside_frames`, `band_db`,
  `band_sd_db`, `rise_start_sample`, `rise_ms` and `rise_db`. With the
  keys taken out every result is 0.0.5's byte for byte.
- A stream's heap no longer grows with its length: at 20 minutes
  without a speaker model, 17.9 MiB where 0.0.5 held 246 MiB.

## 0.0.5

### Added

- Speaker evidence, from utter 0.0.5, with the vosk wheel's surface:
  `SpkModel(path)` with `dim()`, and `KaldiRecognizer(..., spk_model=)`
  or `SetSpkModel`. While one is set, a span of at least 25 pooled
  10 ms frames carries `spk`, `spk_frames`, `spk_start` and `spk_end`
  at the top level and on every word entry. Without one, the output is
  unchanged. The vectors are not the vosk wheel's: profiles are rebuilt
  from the enrolment audio, and the wheel's vectors and thresholds do
  not carry over.
- The release attaches the provenance envelope beside the Sigstore
  bundle.

## 0.0.4

### Fixed

- The floor margin reads no span shorter than the bound, so a quiet
  word's first frames after a pause no longer waive the veto or count
  as silence, and a two-word command is not cut in two. From utter
  0.0.4; the binding is unchanged, and with the margin unset the
  output is identical to 0.0.3.

## 0.0.3

First release, numbered for the utter crate it carries: the wheel's
version is the crate's, and a binding-only fix is a post-release of it.
The binding: a Python binding for the utter crate with the vosk
wheel's surface, `Model` and `KaldiRecognizer`, plus the host endpoint
bound and its floor margin. Wheels for Linux x86_64 and aarch64
(manylinux 2_28 and musllinux 1.2), Windows x64 and arm64, and macOS
x86_64 and arm64, on Python 3.9 and later through the stable ABI, with
a stub and py.typed beside the module. Every wheel carries a
build-provenance attestation, and the release attaches its Sigstore
bundle. `UTTER_VERSION` and `UTTER_REVISION` name the crate the wheel
was built from. A word's `energy_dbfs` is `null` under digital silence
and `floor_dbfs` is absent while the floor is digital silence, as
utter 0.0.3 reports them.
