# Uninstall and disconnect

Use this workflow when the user asks to remove, uninstall, or delete this
package, or to disconnect this device from Beatra entirely.

## The one rule

The device connection (`~/.beatra`) is shared by every installed Beatra skill.
It may only be retired when no other Beatra skill remains on this device — and
`scripts/uninstall.py` is the only component that can decide that. Never delete
`~/.beatra` or any file inside it yourself, and never skip the script, even
when the user asks for a complete removal: if another installed skill still
uses the connection, the connection must survive this uninstall.

## Steps

1. Run the bundled decision script first, while the package files still exist:

   ```
   python3 scripts/uninstall.py
   ```

   `--dry-run` prints the same JSON decision without changing anything or
   contacting the server. Never act on a dry-run report — rerun without the
   flag to actually uninstall.

2. Read the JSON decision it prints:

   - `"decision": "keep_connection"` — another installed skill still uses the
     shared connection (`remaining_skills` lists them), or the inventory could
     not prove this is the last one. The credential and `~/.beatra` stay
     untouched. Tell the user which skills keep the connection alive.
   - `"decision": "disconnected"` — this was the last Beatra skill. The script
     has removed the local connection state. `"revoked": true` means the
     server confirmed the revocation; `"revoked": false` means it could not be
     confirmed from here (server unreachable, or the token was no longer
     recognised) — the authorization then expires on its own after 15 days of
     inactivity, and the user can revoke it immediately in the Beatra Console
     under Agents.
   - `"decision": "revoke_retry"` — the server was reached but refused just
     now (for example rate limiting). Nothing was changed. Run the script
     again shortly, or have the user revoke the device in the Beatra Console
     and then rerun it to finish removing local state.

3. After a `keep_connection` or `disconnected` decision, finish by deleting
   only the package directory the script names in `delete_next`. Do not delete
   anything else. (After `keep_connection`, the inventory notices the deleted
   directory by itself — no further bookkeeping is needed.)

## Disconnecting everything

There is no separate "disconnect all" action. Uninstall each installed Beatra
skill with its own bundled script; the last one automatically revokes the
authorization and clears `~/.beatra`. The user can always revoke the device
from the Beatra Console as well — that invalidates the credential server-side
immediately, whatever remains on disk.
