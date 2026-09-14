# Security

Report a vulnerability through GitHub's private reporting on this
repository, at
<https://github.com/pyscape/utterpy/security/advisories/new>. It
reaches the maintainer alone and is not visible until a fix is
published.

Report it here whether the fault is in the binding or in the decoder
under it. The maintainer is the same for both, and a fix in the utter
crate ships here as a new wheel pinned to the fixed release. A model
file or audio that makes the decoder panic, read out of bounds or
allocate without bound is a vulnerability; so is a Python value that
reaches the crate unchecked, a reference the module holds past the
object that owned it, or a wheel whose contents differ from what the
release workflow built.

## Verifying a release

The release tag is signed with the maintainer's SSH key, the one
GitHub shows as verified on the tag. To check it locally, put that
public key in an allowed-signers file and name the file to git:

```bash
echo "jared@creating.agency $(curl -sf https://github.com/pyscape.keys | grep ssh-ed25519)" >> ~/.ssh/allowed_signers
git config gpg.ssh.allowedSignersFile ~/.ssh/allowed_signers
git tag -v vX.Y.Z
```

Every wheel carries a build-provenance attestation binding it to this
repository, the workflow and the tagged commit, and each release
attaches its Sigstore bundle:

```bash
gh attestation verify <wheel> -R pyscape/utterpy
gh attestation verify <wheel> --bundle utterpy-vX.Y.Z.sigstore.json --owner pyscape
```

## How a report is handled

A report is acknowledged within a few days. The maintainer confirms it,
works a fix privately, and releases it on PyPI; the latest release is
the one fixes go to. The reporter is credited in the release and
the advisory unless they ask to stay anonymous, and their details are
kept private throughout.
