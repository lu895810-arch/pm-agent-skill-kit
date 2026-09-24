#!/usr/bin/env python3
"""Authorize one Beatra Skill package without a local callback listener."""

from __future__ import annotations

import argparse
import json
import os
import re
import secrets
import stat
import socket
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
import webbrowser
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

AUTHORIZATION_ORIGIN = "https://api.beatra.ai"
MCP_URL = "https://mcp.beatra.ai/mcp"
DEVICE_AUTHORIZATION_URL = f"{AUTHORIZATION_ORIGIN}/oauth/device_authorization"
TOKEN_URL = f"{AUTHORIZATION_ORIGIN}/oauth/token"
PACKAGE_SLUG = "beatra"
PACKAGE_DISPLAY_NAME = "Beatra"
PACKAGE_VERSION = "2.8.6"
CLIENT_ID = f"beatra-skill-{PACKAGE_SLUG}"
GRANT_TYPE = "urn:ietf:params:oauth:grant-type:device_code"
SCOPE = (
    "mcp:tools artifacts:write images:generate videos:generate music:generate "
    "speech:generate voices:read voices:write wallet:spend tasks:read artifacts:read tasks:cancel"
)
HTTP_USER_AGENT = f"Beatra-Skill/{PACKAGE_SLUG}/{PACKAGE_VERSION}"
POLL_SECONDS = 5
_PLATFORM_VALUE = re.compile(r"[a-z0-9][a-z0-9._-]{0,63}\Z")
MAX_WAIT_SECONDS = 15 * 60
_UTC = timezone.utc  # noqa: UP017 -- datetime.UTC is unavailable on Python 3.10.

PostForm = Callable[[str, dict[str, str]], tuple[int, dict[str, Any]]]
CredentialProbe = Callable[[Path], bool]
AUTH_REQUIRED_CODE = "BEATRA_AUTH_REQUIRED"
AUTH_REQUIRED_MESSAGE = (
    f"{AUTH_REQUIRED_CODE}: Beatra authorization is no longer valid. "
    "Complete Device Authorization to reconnect."
)
AUTH_IN_PROGRESS_CODE = "BEATRA_AUTH_IN_PROGRESS"
AUTH_IN_PROGRESS_MESSAGE = (
    f"{AUTH_IN_PROGRESS_CODE}: Another Beatra authorization is already in progress. "
    "Complete that approval instead of starting a second one."
)
AUTH_LOCK_TTL_SECONDS = MAX_WAIT_SECONDS + 120
_START_ERRORS = {
    "invalid_client",
    "invalid_request",
    "invalid_scope",
    "invalid_target",
    "server_error",
    "temporarily_unavailable",
}
_TERMINAL_POLL_ERRORS = {
    "access_denied",
    "expired_token",
    "invalid_client",
    "invalid_grant",
    "invalid_request",
    "invalid_target",
    "server_error",
    "temporarily_unavailable",
}


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
        raise RuntimeError(f"Beatra authorization refused HTTP redirect ({code})")


def _default_post_form(url: str, fields: dict[str, str]) -> tuple[int, dict[str, Any]]:
    request = urllib.request.Request(
        url,
        data=urllib.parse.urlencode(fields).encode("utf-8"),
        headers={
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": HTTP_USER_AGENT,
        },
        method="POST",
    )
    opener = urllib.request.build_opener(_RejectRedirectHandler())
    try:
        with opener.open(request, timeout=30) as response:
            status = int(response.status)
            raw = response.read()
    except urllib.error.HTTPError as exc:
        status = int(exc.code)
        raw = exc.read()
    except urllib.error.URLError as exc:
        raise RuntimeError("Beatra authorization service is unreachable") from exc
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Beatra authorization returned HTTP {status}") from exc
    if not isinstance(payload, dict):
        raise RuntimeError(f"Beatra authorization returned HTTP {status}")
    return status, payload


def _private_directory(path: Path) -> None:
    # POSIX gets explicit 700/600. On Windows the state directory lives under
    # the user profile, whose default ACL is already private to the user —
    # the same posture as gh/aws/gcloud credential stores. The former custom
    # DACL ceremony was dropped deliberately: its command patterns read as
    # hostile to agent safety policies and endpoint security, failing installs
    # while adding no protection an elevated administrator could not bypass.
    path.mkdir(mode=0o700, parents=True, exist_ok=True)
    if os.name == "posix":
        path.chmod(0o700)


def _restrict_file(path: Path) -> None:
    if os.name == "posix":
        path.chmod(0o600)


def _atomic_json(path: Path, value: dict[str, Any]) -> None:
    _private_directory(path.parent)
    temporary = path.parent / f".{path.name}.{secrets.token_hex(8)}.tmp"
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, separators=(",", ":"))
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        _restrict_file(temporary)
        os.replace(temporary, path)
        _restrict_file(path)
        if os.name == "posix":
            directory_fd = os.open(path.parent, os.O_RDONLY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
    finally:
        temporary.unlink(missing_ok=True)


def _installation_reference(state_dir: Path) -> str:
    path = state_dir / "installation.json"
    if path.exists():
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
            reference = value["external_installation_ref"]
        except (OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
            raise RuntimeError("Beatra installation state is invalid") from exc
        if not isinstance(reference, str) or not reference.startswith("beatra:"):
            raise RuntimeError("Beatra installation state is invalid")
        _restrict_file(path)
        return reference

    reference = f"beatra:{uuid.uuid4()}"
    _atomic_json(
        path,
        {
            "schema_version": 1,
            "external_installation_ref": reference,
            "created_at": datetime.now(_UTC).isoformat(),
        },
    )
    return reference


def _required_string(payload: dict[str, Any], name: str) -> str:
    value = payload.get(name)
    if not isinstance(value, str) or not value:
        raise RuntimeError("Beatra authorization response is incomplete")
    return value


def _positive_int(payload: dict[str, Any], name: str, default: int) -> int:
    value = payload.get(name, default)
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        return default
    return value


def _validate_verification_url(value: str, *, user_code: str) -> str:
    expected = f"{AUTHORIZATION_ORIGIN}/device#code={urllib.parse.quote(user_code, safe='-')}"
    if value != expected:
        raise RuntimeError("Beatra authorization verification URL is invalid")
    return value


def _existing_credential(state_dir: Path) -> Path | None:
    path = state_dir / "credentials.json"
    try:
        path_stat = os.lstat(path)
        if not stat.S_ISREG(path_stat.st_mode):
            return None
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, TypeError, json.JSONDecodeError):
        return None
    required_strings = (
        "access_token",
        "credential_id",
        "installation_id",
        "scope",
        "authorized_at",
    )
    if (
        not isinstance(value, dict)
        or value.get("schema_version") != 1
        or value.get("mcp_url") != MCP_URL
        or value.get("token_type") != "Bearer"
        or any(not isinstance(value.get(name), str) or not value[name] for name in required_strings)
        or set(value["scope"].split()) != set(SCOPE.split())
    ):
        return None
    _restrict_file(path)
    return path


def _default_probe_credential(credential_path: Path) -> bool:
    import mcp_client

    try:
        mcp_client.verify(state_dir=credential_path.parent)
    except mcp_client.AuthenticationRequired:
        return False
    return True


def _read_authorization_lock(path: Path) -> tuple[dict[str, Any], tuple[int, int]] | None:
    try:
        path_stat = os.lstat(path)
        if not stat.S_ISREG(path_stat.st_mode):
            return None
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, TypeError, json.JSONDecodeError):
        return None
    if (
        not isinstance(value, dict)
        or value.get("schema_version") != 1
        or not isinstance(value.get("owner_nonce"), str)
        or not value["owner_nonce"]
        or isinstance(value.get("created_at"), bool)
        or not isinstance(value.get("created_at"), (int, float))
    ):
        return None
    return value, (path_stat.st_dev, path_stat.st_ino)


def _same_file_identity(path: Path, identity: tuple[int, int]) -> bool:
    try:
        current = os.lstat(path)
    except OSError:
        return False
    return stat.S_ISREG(current.st_mode) and (current.st_dev, current.st_ino) == identity


@contextmanager
def _device_authorization_lock(
    state_dir: Path,
    *,
    wall_time: Callable[[], float],
    lock_nonce: Callable[[], str],
) -> Iterator[None]:
    path = state_dir / ".authorize.lock"
    owner_nonce = lock_nonce()
    if not isinstance(owner_nonce, str) or not owner_nonce:
        raise RuntimeError("Beatra authorization lock owner is invalid")

    descriptor = -1
    owned_identity: tuple[int, int] | None = None
    for attempt in range(2):
        try:
            descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            owned_stat = os.fstat(descriptor)
            owned_identity = (owned_stat.st_dev, owned_stat.st_ino)
            break
        except FileExistsError as exc:
            existing = _read_authorization_lock(path)
            if existing is None:
                raise RuntimeError(AUTH_IN_PROGRESS_MESSAGE) from exc
            payload, identity = existing
            age = wall_time() - float(payload["created_at"])
            if age <= AUTH_LOCK_TTL_SECONDS or not _same_file_identity(path, identity):
                raise RuntimeError(AUTH_IN_PROGRESS_MESSAGE) from exc
            path.unlink()
            if attempt == 1:
                raise RuntimeError(AUTH_IN_PROGRESS_MESSAGE) from exc

    if descriptor < 0:
        raise RuntimeError(AUTH_IN_PROGRESS_MESSAGE)

    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            descriptor = -1
            json.dump(
                {
                    "schema_version": 1,
                    "owner_nonce": owner_nonce,
                    "created_at": wall_time(),
                },
                stream,
                ensure_ascii=False,
                separators=(",", ":"),
            )
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        _restrict_file(path)
        yield
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        if owned_identity is not None and _same_file_identity(path, owned_identity):
            existing = _read_authorization_lock(path)
            if existing is None or existing[0]["owner_nonce"] == owner_nonce:
                path.unlink()


def _safe_protocol_error(value: Any, allowed: set[str]) -> str:
    return value if isinstance(value, str) and value in allowed else "request_failed"


def detect_host_platform(explicit: str | None = None) -> str:
    """The agent environment this process runs inside (docs/device-model.md).

    Order: explicit agent self-report > environment signatures > unknown.
    Detection reads the process environment only — nothing else runs,
    nothing reaches the network.
    """
    if explicit:
        candidate = explicit.strip().lower().replace(" ", "-")
        if _PLATFORM_VALUE.fullmatch(candidate):
            return candidate
    env = os.environ
    if env.get("CLAUDECODE") == "1" or "CLAUDE_CODE_ENTRYPOINT" in env:
        return "claude-code"
    if any(key.startswith("CODEX_") for key in env):
        return "codex"
    ai_agent = env.get("AI_AGENT", "").lower()
    matched = re.match(r"([a-z0-9-]+)_", ai_agent)
    if matched and _PLATFORM_VALUE.fullmatch(matched.group(1)):
        return matched.group(1)
    return "unknown"


def device_display_name() -> str | None:
    """A hostname the user will recognise in the console device list."""
    try:
        name = socket.gethostname().strip()
    except OSError:
        return None
    if not name or not name.isprintable():
        return None
    return name[:120]


def write_host_config(state_dir: Path, *, platform: str, device_name: str | None) -> None:
    """Persist detection results so mcp_client never re-detects per request
    and still has a truth source when its own env detection comes up empty.
    Best-effort: config failure must never block authorization."""
    try:
        payload: dict[str, Any] = {"platform": platform}
        if device_name:
            payload["device_name"] = device_name
        (state_dir / "host.json").write_text(
            json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n",
            encoding="utf-8",
        )
    except OSError:
        pass


def _own_skill_root() -> Path | None:
    """The installed package root this script runs from, when knowable."""
    try:
        return Path(__file__).resolve().parent.parent
    except NameError:
        return None


def record_skill_installation(
    state_dir: Path,
    *,
    platform: str,
    skill_root: Path | None = None,
) -> None:
    """Upsert this package into the device-local skill inventory.

    ~/.beatra/skills.json is the device's own answer to "which skills still
    use this connection". The uninstall flow may only revoke the shared
    credential once this inventory says nothing else is left, so every
    authorization records its package here. Best-effort: inventory failure
    must never block authorization.
    """

    try:
        root = skill_root or _own_skill_root()
        if root is None:
            return
        resolved = str(Path(root).expanduser().resolve())
        path = state_dir / "skills.json"
        entries: list[dict[str, Any]] = []
        if path.exists():
            value = json.loads(path.read_text(encoding="utf-8"))
            loaded = value.get("skills") if isinstance(value, dict) else None
            if isinstance(loaded, list):
                entries = [entry for entry in loaded if isinstance(entry, dict)]
        entries = [
            entry
            for entry in entries
            if not (
                entry.get("slug") == PACKAGE_SLUG and entry.get("install_path") == resolved
            )
        ]
        entries.append(
            {
                "slug": PACKAGE_SLUG,
                "platform": platform,
                "install_path": resolved,
                "recorded_at": datetime.now(_UTC).isoformat(),
            }
        )
        _atomic_json(path, {"schema_version": 1, "skills": entries})
    except (OSError, TypeError, ValueError):
        pass


def _authorize_new_credential(
    *,
    state_dir: Path,
    host_platform: str,
    device_name: str | None,
    post_form: PostForm,
    probe_credential: CredentialProbe,
    open_browser: Callable[[str], bool],
    sleep: Callable[[float], None],
    monotonic: Callable[[], float],
) -> Path:
    external_reference = _installation_reference(state_dir)
    form: dict[str, str] = {
        "client_id": CLIENT_ID,
        "resource": MCP_URL,
        "scope": SCOPE,
        "platform": host_platform,
        "client_name": PACKAGE_DISPLAY_NAME,
        "external_installation_ref": external_reference,
        "package_version": PACKAGE_VERSION,
        "package_slug": PACKAGE_SLUG,
    }
    if device_name:
        form["device_name"] = device_name
    status, created = post_form(DEVICE_AUTHORIZATION_URL, form)
    if status != 200:
        code = _safe_protocol_error(created.get("error"), _START_ERRORS)
        raise RuntimeError(f"Beatra authorization could not start ({code})")

    device_code = _required_string(created, "device_code")
    user_code = _required_string(created, "user_code")
    verification_url = _validate_verification_url(
        _required_string(created, "verification_uri_complete"),
        user_code=user_code,
    )
    interval = max(POLL_SECONDS, _positive_int(created, "interval", POLL_SECONDS))
    server_lifetime = _positive_int(created, "expires_in", MAX_WAIT_SECONDS)
    deadline = monotonic() + min(server_lifetime, MAX_WAIT_SECONDS)

    # The link fragment already carries the approval code, so the page
    # verifies it by itself. Never announce the code separately: the approval
    # page does not display it and the user never types or compares it.
    print(f"Open this Beatra approval page: {verification_url}")
    print(
        "If the browser shows Beatra sign-in first, sign in or create the "
        "account there; the approval page continues automatically. The only "
        "decision on it is selecting Allow."
    )
    print(
        "This helper waits and finishes by itself once the user selects "
        "Allow - no chat confirmation is needed from the user."
    )
    open_browser(verification_url)

    poll_fields = {
        "grant_type": GRANT_TYPE,
        "device_code": device_code,
        "client_id": CLIENT_ID,
        "resource": MCP_URL,
    }
    sleep(interval)
    while monotonic() < deadline:
        status, polled = post_form(TOKEN_URL, poll_fields)
        if status == 200:
            access_token = _required_string(polled, "access_token")
            if polled.get("token_type") != "Bearer":
                raise RuntimeError("Beatra authorization returned an unsupported token type")
            scope = _required_string(polled, "scope")
            if set(scope.split()) != set(SCOPE.split()):
                raise RuntimeError("Beatra authorization returned an unsupported scope")
            credential_path = state_dir / "credentials.json"
            _atomic_json(
                credential_path,
                {
                    "schema_version": 1,
                    "mcp_url": MCP_URL,
                    "token_type": "Bearer",
                    "access_token": access_token,
                    "credential_id": _required_string(polled, "credential_id"),
                    "installation_id": _required_string(polled, "installation_id"),
                    "scope": scope,
                    "authorized_at": datetime.now(_UTC).isoformat(),
                    "idle_expires_in": _positive_int(polled, "idle_expires_in", 15 * 24 * 60 * 60),
                },
            )
            access_token = ""
            print("Beatra authorization saved to the private credential file.")
            if not probe_credential(credential_path):
                credential_path.unlink(missing_ok=True)
                raise RuntimeError(AUTH_REQUIRED_MESSAGE)
            print("Beatra is ready.")
            return credential_path

        error = polled.get("error")
        if error not in {"authorization_pending", "slow_down"}:
            safe_code = _safe_protocol_error(error, _TERMINAL_POLL_ERRORS)
            raise RuntimeError(f"Beatra authorization stopped ({safe_code})")
        if error == "slow_down":
            interval = max(interval + 5, _positive_int(polled, "interval", interval))
        sleep(interval)

    raise RuntimeError("Beatra authorization timed out after 15 minutes")


def authorize(
    *,
    state_dir: Path | None = None,
    platform: str | None = None,
    skill_root: Path | None = None,
    force: bool = False,
    post_form: PostForm = _default_post_form,
    probe_credential: CredentialProbe = _default_probe_credential,
    open_browser: Callable[[str], bool] = webbrowser.open,
    sleep: Callable[[float], None] = time.sleep,
    monotonic: Callable[[], float] = time.monotonic,
    wall_time: Callable[[], float] = time.time,
    lock_nonce: Callable[[], str] = lambda: secrets.token_hex(16),
) -> Path:
    """Ensure that the one shared Beatra credential is live and ready."""

    state_dir = (state_dir or Path.home() / ".beatra").expanduser()
    _private_directory(state_dir)
    host_platform = detect_host_platform(platform)
    device_name = device_display_name()
    write_host_config(state_dir, platform=host_platform, device_name=device_name)
    record_skill_installation(state_dir, platform=host_platform, skill_root=skill_root)
    if not force and (credential_path := _existing_credential(state_dir)):
        if probe_credential(credential_path):
            print("Beatra is ready with the existing private credential.")
            return credential_path
        credential_path.unlink(missing_ok=True)

    with _device_authorization_lock(
        state_dir,
        wall_time=wall_time,
        lock_nonce=lock_nonce,
    ):
        return _authorize_new_credential(
            state_dir=state_dir,
            host_platform=host_platform,
            device_name=device_name,
            post_form=post_form,
            probe_credential=probe_credential,
            open_browser=open_browser,
            sleep=sleep,
            monotonic=monotonic,
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=f"Authorize the {PACKAGE_DISPLAY_NAME} Skill")
    parser.add_argument(
        "--platform",
        default=None,
        help=(
            "Name of the agent environment running this install (for example "
            "claude-code, codex, workbuddy). Detected from the environment "
            "when omitted."
        ),
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Start a new Beatra Device Authorization even when a credential exists.",
    )
    args = parser.parse_args()
    try:
        authorize(platform=args.platform, force=args.force)
    except RuntimeError as exc:
        print(str(exc), file=os.sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
