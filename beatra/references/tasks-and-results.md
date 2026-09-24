# Tasks and results

Generation returns an asynchronous task. Keep its `task_id` and use
`beatra.tasks.get` to poll it with bounded backoff: wait 2 seconds before the
first poll, then increase the interval toward 5, 10, and at most 15 seconds.
Honor `deadline_at` when the task response provides it. Otherwise stop active
polling after 30 minutes, report the task ID and current status, and explain
that the user or a later agent session can resume polling the same task.

## Interpret state

- `queued` and `running` are nonterminal. Continue polling; do not submit a
  replacement generation.
- `succeeded`, `failed`, and `canceled` are terminal. Stop polling.
- On success, present returned artifacts, resolved model, actual usage, and
  billing truth. For prepaid work, report `billing.net_charged_credits`; the gross charged value
  may include a supplemental actual-usage debit and the refunded value may
  return an unused request-time estimate.
- For a settled video task, `usage.video_seconds` is the authoritative
  billable total. When present, `usage.input_video_seconds` and
  `usage.output_video_seconds` are the authoritative components of that total.
  This distinction matters for reference-video generation and video editing,
  where both input and output can be billable. Do not infer either component
  when Beatra returns it as `null`.
- On failure, preserve the structured error and apply the recovery reference.

Use `beatra.tasks.list` to recover a lost task ID or inspect recent work from
this connection. Filter only when doing so helps identify the task.

Call `beatra.tasks.cancel` only when the user requests cancellation. Before
remote execution starts, cancellation stops the task. After remote execution
starts, Beatra returns `canceled` only when the stop is confirmed. A `409`
means the task continues: do not promise a stop or refund, do not submit a
replacement, and continue polling the same task.

Do not infer an artifact URL, completion, usage, or charged credits from
elapsed time. Return only fields present in Beatra's task response.
For MCP task reads, prefer the direct `structuredContent.usage` and
`structuredContent.billing` objects; the complete envelope remains available
under `structuredContent.task`.
