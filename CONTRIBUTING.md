# Contributing

## Proposing a change

Open an issue for anything larger than a small fix, so the approach can
be agreed before the work. Changes reach `main` through a pull request;
`main` is protected, and a request merges only when every check has
passed and the branch is current.

The binding follows the vosk wheel's surface. A method that the vosk
wheel has keeps its name and shape here; a method it lacks is a decision
for the utter crate first, recorded there, and bound here after.

## What a change must satisfy

The checks below run in CI and each one blocks a merge. Run them before
opening the request, from a venv with `pip install --require-hashes -r
.github/requirements/lint.txt` and `pip install .`:

- `cargo fmt --check`
- `cargo clippy --release --all-targets -- -D warnings`
- `ruff check python tests` and `ruff format --check python tests`
- `mypy --strict tests` and `python -m mypy.stubtest utterpy`, so the
  stub and the binary agree
- `pytest tests` against a stock model, with `UTTER_TEST_MODEL` naming
  its directory; without one `python tests/smoke.py` checks the surface
- `typos`, `yamllint --strict .`, markdownlint and taplo over the prose
  and configs

A new method comes with a stub entry, a line in the smoke test's surface
list, and a test against the model.

Comment only what the code cannot say. A comment that restates the code
is removed; a rule that lives elsewhere is cited, not repeated.

## Releasing

A release is a signed tag on `main`. Before the tag, one pull request
bumps `version` in both pyproject.toml and Cargo.toml, moves the
changelog's Unreleased section under the new number, and adds
`docs/release-notes/vX.Y.Z.md`, the release body. The version job on
the tag checks all four and that the tag's signature is one GitHub
verifies for the maintainer:

```sh
git tag -s vX.Y.Z -m "utterpy X.Y.Z"
git push origin vX.Y.Z
```

The workflow then builds every wheel and the sdist, attests them,
attaches them and the Sigstore bundle to a GitHub release, and
publishes to PyPI through trusted publishing from the `pypi`
environment, which deploys from `v*` tags only. Before the first
release, PyPI needs a pending publisher for the project name naming
this repository, `wheels.yml` and the `pypi` environment; the first
publish then creates the project. No token lives in the repository.
A tag that reaches PyPI cannot be moved or deleted; a fix is the next
version.

## Certifying origin

Contributions are certified under the Developer Certificate of Origin,
<https://developercertificate.org>: by signing off a commit you assert
you wrote the change or may submit it under the project's license. Add
the line with `git commit -s`:

```text
Signed-off-by: Your Name <you@example.com>
```

## License

The binding is MIT. A contribution is offered under the same terms.
