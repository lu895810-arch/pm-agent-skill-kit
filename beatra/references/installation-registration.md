# Installation registration

On first use, the bundled client makes a best-effort non-billable
`beatra.installations.register` call for this package. Registration records the
package slug, version, platform, and stable external installation reference; it
does not replace Device Authorization and never asks for narrower package
scopes.

The non-secret `~/.beatra/registrations.json` cache suppresses another
registration until the package version or agent environment changes or
24 hours pass. Registration failure must never block the user's requested
creative task. An unknown but well-formed package slug is accepted and
recorded as unrecognized so package release never depends on a synchronized
backend registry deployment.

The `platform` field is the real agent environment, resolved once per process
from environment signatures (or `~/.beatra/host.json`, written at
authorization time) — never detected per request. When authorizing manually,
pass `--platform <environment-name>` to `scripts/authorize.py` if automatic
detection cannot identify the host.
