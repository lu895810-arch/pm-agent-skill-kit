# Automatic updates and safety

The bundled client checks for a newer release for the installed package channel before ordinary Beatra commands, at most once every 24 hours. The check is silent and enabled by default so it does not interrupt the user's requested work. When a higher version is available, the client installs it automatically without separate confirmation.

Updates are accepted only from the fixed official Beatra discovery address and immutable Beatra CDN path for the package's embedded channel and locale. The client refuses redirects, version downgrades, a different package, a different channel or locale, an unexpected URL, an unsafe archive, and files outside the package-owned destination.

Before package files are replaced, the client verifies the discovery document, manifest checksum, archive checksum, and every packaged file's size and checksum. It replaces only files owned by the installed package. Replacement uses a lock, staging files, backups, a recovery journal, and rollback. The updater replaces its own client file last.

If checking, downloading, verification, replacement, rollback, or recovery fails, the currently usable installation remains in place and the user's original command continues. A failed update must never be treated as a reason to resubmit a paid generation request.

Automatic updates are controlled per installation and the choice persists across later commands:

```text
python3 scripts/mcp_client.py update --auto off
python3 scripts/mcp_client.py update --auto on
python3 scripts/mcp_client.py update --check
```

`--auto off` disables silent checks for this installation. `--auto on` restores the default. `--check` reports the official available version without replacing files. Running `python3 scripts/mcp_client.py update` performs an immediate verified update. If `python3` is not the local Python command, use the available Python 3.10+ command.
