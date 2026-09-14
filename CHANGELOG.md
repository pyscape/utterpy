# Changelog

Notable changes to the wheel, newest first. The project follows semantic
versioning; release dates are recorded by the git tags and the GitHub
releases.

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
