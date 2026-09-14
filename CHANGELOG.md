# Changelog

Notable changes to the wheel, newest first. The project follows semantic
versioning; release dates are recorded by the git tags and the GitHub
releases.

## Unreleased

First release: a Python binding for the utter crate with the vosk
wheel's surface, `Model` and `KaldiRecognizer`, plus the host endpoint
bound and its floor margin. Wheels for Linux x86_64 and aarch64
(manylinux 2_28 and musllinux 1.2), Windows x64 and arm64, and macOS
x86_64 and arm64, on Python 3.9 and later through the stable ABI, with
a stub and py.typed beside the module. Every wheel carries a
build-provenance attestation, and the release attaches its Sigstore
bundle.
