#!/usr/bin/env python3
"""Uninstall one Beatra Skill package without stranding the shared connection.

The device connection (~/.beatra) is shared by every installed Beatra skill.
Removing one skill must therefore never touch the shared credential while any
other skill still uses it — even when the user asks for a complete removal.
Only when this device's skill inventory says nothing else is left does the
credential revoke itself and the local state leave with it.

Every uncertain situation resolves to "keep the connection": a wrongly kept
credential idles out server-side after 15 days and can be revoked from the
Console at any time, while a wrongly revoked one breaks every remaining skill.

This script never deletes the package directory it runs from — it reports the
directory so the calling agent can remove it as the final step.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Callable

AUTHORIZATION_ORIGIN = "https://api.beatra.ai"
REVOKE_URL = f"{AUTHORIZATION_ORIGIN}/oauth/device/revoke"
PACKAGE_SLUG = "beatra"
PACKAGE_DISPLAY_NAME = "Beatra"
PACKAGE_VERSION = "2.8.6"
HTTP_USER_AGENT = f"Beatra-Skill/{PACKAGE_SLUG}/{PACKAGE_VERSION}"

#: Everything the connection owns inside ~/.beatra. Removal unlinks exactly
#: these and then removes the directory only if it is empty — the script
#: never recursively deletes a directory it does not fully understand.
_STATE_FILES = (
    "credentials.json",
    "installation.json",
    "host.json",
    "skills.json",
    "registrations.json",
)

PostRevoke = Callable[[str], int]


class _RejectRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(
        self,
        _request: urllib.request.Request,
        _file_pointer: Any,
        code: int,
        _message: str,
        _headers: Any,
        _new_url: str,
    ) -> None:
        raise RuntimeError(f"Beatra revocation refused HTTP redirect ({code})")


def _default_post_revoke(token: str) -> int:
    request = urllib.request.Request(
        REVOKE_URL,
        data=b"",
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
            "User-Agent": HTTP_USER_AGENT,
        },
        method="POST",
    )
    opener = urllib.request.build_opener(_RejectRedirectHandler())
    try:
        with opener.open(request, timeout=30) as response:
            return int(response.status)
    except urllib.error.HTTPError as exc:
        return int(exc.code)
    except urllib.error.URLError as exc:
        raise RuntimeError("Beatra authorization service is unreachable") from exc


def _own_skill_root() -> Path | None:
    """The installed package root this script runs from, when knowable."""
    try:
        return Path(__file__).resolve().parent.parent
    except NameError:
        return None


def _load_inventory(state_dir: Path) -> tuple[list[dict[str, Any]] | None, str]:
    """Return (entries, state) where state names why entries may be None."""

    path = state_dir / "skills.json"
    if not path.exists():
        return None, "inventory_missing"
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None, "inventory_unreadable"
    loaded = value.get("skills") if isinstance(value, dict) else None
    if not isinstance(loaded, list):
        return None, "inventory_unreadable"
    return [entry for entry in loaded if isinstance(entry, dict)], "ok"


def _device_token(state_dir: Path) -> str | None:
    path = state_dir / "credentials.json"
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    token = value.get("access_token") if isinstance(value, dict) else None
    if not isinstance(token, str) or not token:
        return None
    return token


def _provably_deleted(install_path: str) -> bool:
    """True only when the entry's directory is verifiably gone.

    "Not currently visible" is not "uninstalled": an unmounted volume, a
    permission-restricted parent, or any stat error must count the skill as
    alive — the rule resolves every uncertainty to keeping the connection.
    Only a clean missing entry under a reachable parent is proof of removal.
    """

    try:
        os.stat(install_path)
        return False
    except FileNotFoundError:
        pass
    except OSError:
        return False
    parent = os.path.dirname(install_path.rstrip("/\\")) or os.sep
    try:
        os.stat(parent)
    except OSError:
        return False
    return True


def _remove_local_state(state_dir: Path) -> None:
    for name in _STATE_FILES:
        try:
            (state_dir / name).unlink(missing_ok=True)
        except OSError:
            pass
    try:
        state_dir.rmdir()
    except OSError:
        pass


def uninstall(
    *,
    state_dir: Path | None = None,
    skill_root: Path | None = None,
    post_revoke: PostRevoke = _default_post_revoke,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Apply the last-skill rule and return a machine-readable decision."""

    state_dir = (state_dir or Path.home() / ".beatra").expanduser()
    root = skill_root or _own_skill_root()
    resolved_root = str(Path(root).expanduser().resolve()) if root is not None else None

    result: dict[str, Any] = {
        "package": PACKAGE_SLUG,
        "dry_run": dry_run,
        "delete_next": resolved_root,
    }

    if not state_dir.is_dir():
        # Nothing local to retire; the package files are all that is left.
        result.update({"decision": "disconnected", "revoked": False, "reason": "no_local_state"})
        return result

    if resolved_root is None:
        result.update({"decision": "keep_connection", "reason": "unknown_install_path"})
        return result

    try:
        entries, inventory_state = _load_inventory(state_dir)
        if entries is None:
            # No trustworthy inventory means no proof this is the last skill —
            # the connection stays, and the 15-day idle expiry backstops it.
            result.update({"decision": "keep_connection", "reason": inventory_state})
            return result

        survivors: list[dict[str, Any]] = []
        for entry in entries:
            if (
                entry.get("slug") == PACKAGE_SLUG
                and entry.get("install_path") == resolved_root
            ):
                continue  # the package being uninstalled
            install_path = entry.get("install_path")
            if isinstance(install_path, str) and install_path and _provably_deleted(install_path):
                continue  # verifiably removed outside this flow — self-heal
            survivors.append(entry)
    except Exception:  # noqa: BLE001 -- any surprise resolves to keeping the
        # connection; a crash here must never read as permission to revoke.
        result.update({"decision": "keep_connection", "reason": "inventory_error"})
        return result

    if survivors:
        # The inventory is deliberately not rewritten here: this package's own
        # entry disappears through the provably-deleted check once the agent
        # finishes removing the directory, so an interrupted uninstall leaves
        # a still-installed skill visible rather than silently forgotten.
        result.update(
            {
                "decision": "keep_connection",
                "reason": "other_skills_still_installed",
                "remaining_skills": [
                    {"slug": entry.get("slug"), "platform": entry.get("platform")}
                    for entry in survivors
                ],
            }
        )
        return result

    if dry_run:
        result.update({"decision": "disconnected", "revoked": False, "reason": "dry_run"})
        return result
    token = _device_token(state_dir)
    revoked = False
    revoke_state = "no_credential"
    if token is not None:
        try:
            status = post_revoke(token)
            if status == 200:
                revoked = True
                revoke_state = "revoked"
            elif status == 401:
                # The server no longer recognises this token; the local copy
                # is worthless either way, but nothing was confirmed revoked.
                revoke_state = "not_recognized"
            else:
                # Reached but refused (rate limit, server error): keep every
                # local file so a retry — or a Console revoke followed by a
                # rerun — can still finish the job cleanly.
                result.update(
                    {
                        "decision": "revoke_retry",
                        "revoked": False,
                        "reason": f"http_{status}",
                    }
                )
                return result
        except RuntimeError:
            revoke_state = "unreachable"
    token = None
    _remove_local_state(state_dir)
    result.update({"decision": "disconnected", "revoked": revoked, "reason": revoke_state})
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description=f"Uninstall the {PACKAGE_DISPLAY_NAME} Skill from this device"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report the decision without revoking or changing any file.",
    )
    args = parser.parse_args()
    result = uninstall(dry_run=args.dry_run)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.dry_run:
        print("Dry run: nothing was changed. Run without --dry-run to uninstall.")
        return 0
    if result["decision"] == "keep_connection":
        print(
            "The shared Beatra connection stays in place"
            + (
                " because other installed skills still use it."
                if result.get("reason") == "other_skills_still_installed"
                else " because this device's skill inventory could not prove it is unused."
            )
        )
    elif result["decision"] == "revoke_retry":
        print(
            "Nothing was changed: the Beatra server refused the revocation just now. "
            "Run this script again shortly, or revoke the device in the Beatra "
            "Console and rerun to finish removing local state."
        )
        return 0
    elif result.get("revoked"):
        print("The Beatra device authorization is revoked and local state is removed.")
    else:
        print(
            "Local state is removed. The server-side authorization could not be "
            "confirmed revoked from here; it expires after 15 days of inactivity "
            "and can be revoked in the Beatra Console at any time."
        )
    if result.get("delete_next"):
        print(f"Finish by deleting the package directory: {result['delete_next']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
