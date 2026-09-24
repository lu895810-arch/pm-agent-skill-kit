# MCP connection

All Beatra Skill packages use one connection path:

```text
scripts/mcp_client.py -> https://mcp.beatra.ai/mcp
```

They share the one full-scope Device Token stored in
`~/.beatra/credentials.json`. Installing or switching packages must not trigger
another authorization when that credential is already valid. Do not add,
enable, trust, or configure a host Beatra Connector. Never print or move the
token into command arguments, environment variables, logs, chat, or another
package directory.

The bundled client performs MCP `initialize`, retains `MCP-Session-Id` when the
server returns one, sends `notifications/initialized`, and then uses
`tools/list` or `tools/call`. Its `verify` command runs the non-billable
`beatra.tasks.list` operation. It supplies the private `Authorization: Bearer`
header on every request without exposing its value.

Source attribution: every `tools/call` may carry two optional string
arguments, `source_package_slug` (this package's slug) and `source_platform`
(the agent environment, for example `claude-code` or `codex`). The bundled
client adds them automatically. They are telemetry only: missing values never
block a call, and the server treats them as `unknown`.
