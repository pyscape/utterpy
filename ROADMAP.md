# Roadmap

Direction for roughly the next year. It is intent, not a commitment to
dates. The binding's direction is the crate's; utter's
[roadmap](https://github.com/pyscape/utter/blob/main/ROADMAP.md) says
where the decoder is going, and this file says what the wheel does
about it.

## Where the project is

Not yet on PyPI. The binding covers the vosk wheel's surface plus the
host endpoint bound and its floor margin, builds wheels for Linux,
Windows and macOS on every push, and runs its tests on Python 3.9 to
3.14. The first release ships against the next release of utter.

## Planned

- **The first PyPI release**, through trusted publishing, with every
  wheel attested and the release carrying its Sigstore bundle.
- **Track each utter release.** A crate release is followed by a wheel
  pinned to it, with the changelog naming what changed for a Python
  host. The pin is a version on crates.io, never a commit.
- **Reach 0.1 with the crate.** The Python surface keeps the vosk
  wheel's shape; a breaking change before 0.1 follows one in the crate
  and is named in the changelog. After 0.1 the API settles.

## Not planned

- **A surface the crate does not have.** A method the vosk wheel lacks
  is a decision for utter first; the binding does not front-run it.
- **Runtime dependencies.** The wheel is one extension module and a
  stub; it stays that way.
