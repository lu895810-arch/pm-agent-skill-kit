# Installation and authentication

Use this reference when Beatra is newly installed, unavailable, or needs its
authorization recovered. This flow is owned by the Skill and works the same way
in any agent that can run Python 3.10 or newer and make HTTPS requests. The
helpers use only the Python standard library; do not install packages for them.

## Keep one private local identity

The Skill uses two user-only files:

- `~/.beatra/installation.json` contains one stable, non-secret installation
  reference.
- `~/.beatra/credentials.json` contains the single Device Token.

On POSIX systems the directory must be mode `0700` and both files mode `0600`.
On Windows the current user must be the only principal granted access through
the file ACL. Never copy the Device Token into conversation context, stdout,
stderr, a command argument, an environment variable, a log, a backup, a diff,
or another file. A completed authorization leaves the token only in
`~/.beatra/credentials.json`.

## Ensure Beatra is ready

From the installed `beatra` Skill directory, run:

```text
python3 scripts/authorize.py
```

Use `python` instead when that is the local Python 3.10+ command. Always run this
idempotent helper after installing or replacing a Beatra Skill and when
recovering its connection. It validates the candidate credential with one
non-billable live MCP request. A valid credential becomes Ready without opening
the browser, so installing another Beatra package does not require a second
approval.

When no valid credential exists, or the live MCP endpoint definitively returns
HTTP 401, the helper:

1. reuses or creates `~/.beatra/installation.json`;
2. requests a Device Authorization from Beatra;
3. opens the returned HTTPS approval page in the user's browser and also shows
   its URL. The URL fragment carries the approval code, so the page verifies
   the code by itself;
4. polls every 5 seconds for up to 15 minutes while the user signs in (or
   creates their account) and selects Allow;
5. atomically saves the returned Device Token to
   `~/.beatra/credentials.json` without printing an HTTP response body;
6. validates the new credential with the same non-billable MCP request and
   prints Ready only after it succeeds.

When telling the user what to do:

- present the approval page as a link and say the only decision on it is
  selecting Allow;
- never quote, display, or read out the approval code. It travels inside the
  link fragment, the approval page does not show it, and the user never types
  or compares it — a code surfaced in conversation is noise, not a step;
- say prominently that a signed-out browser lands on Beatra sign-in first:
  the user signs in or creates their account there, and the approval page
  continues automatically after sign-in;
- say once that the connection continues automatically after Allow, then
  detect completion yourself — never ask the user to confirm in chat that
  they approved.

Approval legitimately takes minutes when sign-in or account creation is
involved, so run the helper in the background when the command runner enforces
a shorter timeout. Completion is observable without the user's help: the
helper exits by itself after printing Ready, and a non-billable
`python3 scripts/mcp_client.py verify` succeeds once the credential lands.

The helper opens no local listener and requires no inbound connection. One
approval covers image, video, music, speech, upload, model, and task tools.

HTTP 403 or insufficient scope does not prove the credential is invalid. Keep
the credential and run `python3 scripts/authorize.py --force` only when the user
explicitly wants to reconnect or switch accounts. A timeout, DNS/TLS failure,
HTTP 429, or HTTP 5xx is transient: keep the credential, do not start Device
Authorization, and retry after connectivity recovers.

## Use the bundled MCP client

Every Beatra Skill tool runs through the bundled `scripts/mcp_client.py`, which
connects to `https://mcp.beatra.ai/mcp`. Do not add, enable, trust, or configure
a host Beatra Connector. The bundled client reads the shared credential file
and never accepts the token through argv or the environment:

```text
python3 scripts/mcp_client.py verify
python3 scripts/mcp_client.py tools
python3 scripts/mcp_client.py call beatra.tasks.list
```

For `call`, provide the tool arguments as one JSON object on stdin. Do not put
user content or credentials in the command arguments. The authorization helper
already performs this verification. Run the explicit `verify` command only for
diagnostics; it invokes `beatra.tasks.list` with `{}` and is non-billable.

The direct client follows the Streamable HTTP sequence:

1. send `initialize` with the MCP protocol version and client information;
2. retain an `MCP-Session-Id` response header when the server provides one;
3. send the `notifications/initialized` notification;
4. use `tools/list` for discovery and `tools/call` for execution;
5. include the protocol version, optional session ID, and Device Token bearer
   header on every request.

## Recover or revoke access

The single Device Token has a sliding 15-day idle lifetime. Every accepted MCP
use extends that idle deadline without user action. If Beatra returns HTTP 401
after the token was idle too long or was revoked, rerun `scripts/authorize.py`;
the helper replaces and validates the credential. Do not start another
authorization for a media-type change and do not delete a credential because of
a transient connection failure.

The user can revoke a connected agent from the Beatra Console at any time.
Revocation immediately invalidates the credential. Rerun Device Authorization
only when the user wants to reconnect that installation.

After first installing or replacing the Skill, start a new agent session when
the host discovers Skills only at session startup.
