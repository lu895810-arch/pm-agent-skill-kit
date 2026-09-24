# Public social data

Look up public posts, notes, videos, accounts, comments, and trends. Do not
invent an `operation_key`. Live tools, arguments, and credit prices come from
`beatra.social.tools.search` and `beatra.social.tools.get` on this connection.
If those tools are not exposed, say they are not available on this connection.
Do not invent a key, call `beatra.models.list`, or turn the lookup into
generation. Continue only with media the user already asked for.

Supported `platform` values are `tiktok`, `douyin`, `xiaohongshu`, `instagram`,
`youtube`, and `twitter`. Supported `capability_family` values are `content`,
`creator`, `comments`, `trends`, and `captions`. Captions exist only when the
live catalog returns them. Search with `query`, `platform`,
`capability_family`, optional `limit`, and optional `cursor`; do not invent a
`type` argument.

## Golden path

1. Search with `beatra.social.tools.search` by `query`, `platform`, or
   `capability_family`. This call is not billable. Page search results with
   the returned `next_cursor`.
2. Inspect one result with `beatra.social.tools.get`. This call is not
   billable. Read the arguments, credit price, and `schema_hash`.
3. Copy the `schema_hash` that this `tools.get` just returned.
4. Call `beatra.social.execute` once with `operation_key`, that
   `schema_hash`, `arguments`, and one `client_request_id`.
5. Poll that task with `beatra.tasks.get`.

One `execute` is one prepaid lookup and one asynchronous task. The next page
of looked-up results is another `execute`, not a page token on the same call.

## Confirmation and identity

A direct, well-specified request to look up authorizes that exact paid
`execute` once. Otherwise show the `operation_key` and the credit price
returned by `tools.get` before execution. Do not show `schema_hash`. Do not
ask for a model. Public social lookup has no `model` field.

Create `client_request_id` only after the execute payload is final. An
identical retry keeps the same ID and the exact `operation_key`,
`schema_hash`, and `arguments`. Any accepted change needs a new ID and
confirmation.

## Delivery and recovery

The result is inline JSON or a JSON artifact. Deliver the returned payload,
`task_id`, terminal status, and `billing.net_charged_credits`. Do not look
for a resolved model or a generated media file.

If the task ID is lost, list plausible tasks and compare each detailed
`operation_key`, arguments, and `schema_hash` with the saved payload.

On a failed lookup, keep `error.code` and read the platform wording in
`error.message` or `error.data.message`. Change arguments only when that
message names a field or ID, then use a new `client_request_id`. Otherwise
keep the same ID and the same payload. Do not suggest changing a model.

Read video frames or spoken audio with the host's native understanding.
These tools only look up public data.
