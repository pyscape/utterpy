# Governance

## Roles

The project has a single maintainer, the same as the utter crate's, who
reviews and merges changes, cuts releases, and answers issues and
vulnerability reports. Anyone may contribute through a pull request
under [CONTRIBUTING.md](CONTRIBUTING.md).

## How decisions are made

The binding follows the crate. A design decision about decoding, the
JSON output or the endpoint rules belongs to the utter crate and is
recorded in its
[decision records](https://github.com/pyscape/utter/tree/main/docs/td);
the binding exposes what a record settles. What the binding decides for itself is narrow: the
Python surface keeps the vosk wheel's names and shapes, the wheel has
no runtime dependencies, the pin moves to a released crate only, never
to a commit, and the wheel's version is the crate's, with a
binding-only fix shipped as a post-release of that number. A change to one of those is made in this file and
in [CONTRIBUTING.md](CONTRIBUTING.md), not in a pull request alone.

The maintainer makes the final call on a change. Disagreement is
resolved in the issue or pull request, on the evidence: the crate's
decision records, the tests against the stock model, and the stub
check that keeps the typed surface honest.

## Changes to this model

As the project gains maintainers, this file records how roles and
decisions are shared. Until then, the model is as stated above.
