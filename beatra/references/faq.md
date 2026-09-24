# Beatra questions and anti-patterns

Symptoms a user reports, and the practice each one calls for. The procedures
themselves live in the per-medium references and the shared runtime documents;
this file routes a symptom to the right one and names the habits that spend
credits on a guess.

## The user says the result does not match what they asked for

Name which of the three causes it is before offering to remake anything.

**Wording was added that the user never gave.** Style, lighting, mood,
instrumentation, or camera language introduced during expansion is the usual
reason a result feels unlike the brief. Say which words were added, restore the
user's own subject, constraints, and negations, and only then offer a new
request. See [images](images.md), [videos](videos.md), and [music](music.md)
for what each route legitimately has to add — a named artist in a music prompt,
for example, must be replaced with musical qualities.

**The route was wrong for the request.** A base-preserving edit asked of a
generate call, or a text-to-video route used when a usable still existed, comes
back plausible and off-brief. Re-read the smallest-path rules in the main
instructions and pick the route that matches the input the user actually has.

**The prompt and route were right and the model missed.** This is a reportable
outcome, not something to hide behind a reworded retry. Report it, and let the
user decide whether to spend again.

A returned result that does not match the prompt is always worth stating
plainly. Silently resubmitting a reworded prompt bills the user for a defect
they were never told about.

## The user names a model and the request is refused

Respect the concrete choice and report the incompatibility. Do not substitute a
different model or drop the unsupported control to make the call succeed — a
result from a model the user did not choose is a worse outcome than a clear
refusal.

Read the live interface card with `beatra.models.list` for that route's exact
capability before saying anything about compatibility, price, duration, or
supported controls. Model, price, language, default, and reference-limit facts
change on the server and are never maintained from memory. See
[models](models.md).

## An optional control changes which model runs

Sending an explicit value for an optional control is itself a filter. With
`model: "auto"`, an explicit `true` **or** `false` on a control such as
`enhance_prompt` narrows the eligible set to models that expose it, so a request
that would have routed one way silently routes another. An explicitly named
model that does not expose the control rejects the request outright.

Send an optional control only when the selected model's interface card lists it.
Omitting it is not the same as sending `false`. See [images](images.md) for the
image-side detail, and note that `beatra.videos.enhance_prompt` is a separate
paid tool that rewrites a brief by design, not a control.

## The user asks why a video needs a top-up when an image did not

A direct, well-specified request authorizes one paid image, music, speech, or
social execute, and one gift-sized video-prompt or keyframe stage. It does not
authorize `beatra.videos.generate`, `animate`, `interpolate`,
`generate_from_references`, `edit`, `extend`, or `beatra.voices.clone`.

Those need the six-field production card in the main instructions first,
carrying that route's tool name, its live-card duration, resolution and aspect,
and the provisional estimate. Planning, comparison, or “make the clip” is not
approval. Do not create a `client_request_id` until the user approves the card,
and do not ask them to confirm they have enough credits — the connection
reports the balance itself.

## The run stops on insufficient balance

Relay the returned public message and keep its top-up URL exact, translating
the rest. That message is the authority on where to add credits; do not
substitute a remembered address.
Say that nothing was charged only when the error itself says so. Retry the same
frozen `client_request_id` with the same payload once the user says they have
topped up — a new ID here would be new paid work.

When the user asks what to buy, send them to the top-up page the returned
message links to and let its live amounts answer; do not quote a tier from
memory, because a remembered amount goes stale silently. The signup gift
usually cannot start a video or a voice clone, so a first-time user who
reaches this error normally needs the starter tier rather than the smallest
amount on offer. Do not push the largest tier.

Read the balance with `beatra.wallet.get` and what was actually charged with
`beatra.wallet.ledger`. Both are free reads available at any time. Never invent
a top-up operation or any other account mutation. See
[billing, errors, and recovery](billing-errors-and-recovery.md).

## A task is queued or running longer than expected

Queued and running are normal states, not failures. Honor a returned
`deadline_at`; otherwise stop active polling after 30 minutes, report the
current task state and how to resume, and leave the work running. A slow task is
never a reason for a second submission — that bills twice for one result. See
[tasks and results](tasks-and-results.md).

## The create response is lost

Do not resubmit blind. Use `beatra.tasks.list` with a plausible capability, then
`beatra.tasks.get` on every plausible candidate: list items omit the full input,
so compare each detailed `task.input` against the saved payload — resolved
model, media, and options for generation, or `operation_key`, arguments, and
`schema_hash` for a social lookup.

Only a genuinely unknown outcome justifies repeating the request, and then only
the identical frozen payload under the original `client_request_id`. An
ambiguous match, a queued task, or a running task never authorizes a
replacement.

## A public social lookup fails

Keep `error.code` and read the platform's own wording in `error.message` or
`error.data.message`. Change arguments only when that message names a field or
ID, and use a new `client_request_id` when you do; otherwise keep the same ID
and the same payload.

A social failure is not a model event. Do not call `beatra.models.list`, do not
suggest changing a model, and do not turn the lookup into generation. Copy
`schema_hash` from `beatra.social.tools.get` into execute rather than carrying
it, and never invent an `operation_key`. See
[public social data](social.md).

## The user wants a voice cloned

Voice cloning is the one route with a rights gate before the upload. Obtain
explicit confirmation that the user owns the voice or has the owner's
permission, show the production card, and only then set
`consent_attested: true`. Ordinary media upload has no equivalent step, so do
not add one. See [uploads](uploads.md) and
[speech and voices](speech-and-voices.md).

## The user asks whether a returned file is any good

Report only what the host can actually see. When a result cannot be rendered or
played, deliver the artifact, say plainly that it has not been inspected, and
give the user the brief to check against. A confident review of a file the host
never opened is the most expensive error in this package, because the user
publishes it.

Report the `task_id`, terminal status, every returned result, the resolved model
for generation, and `billing.net_charged_credits`. Include gross charge and
refund only when present.

## Anti-patterns

**Read the live card; do not answer from memory.** Model availability, price,
duration limits, supported controls, and reference limits are server truth.
A remembered price quoted to a user is wrong on the day the server changes it.

**Send an optional control only when the card lists it.** Omitting a control and
sending `false` are different requests, and the difference silently changes
which model runs.

**Carry the user's wording; disclose what you add.** Expansion is allowed only
as far as the route needs, and whatever was added gets said out loud.

**Submit once per `client_request_id`.** Reconcile with `beatra.tasks.list`
before ever repeating a paid call. A lost response is an unknown, not a
failure.

**Upload through the bundled client.** Never send a filesystem path to a
generation tool, use host HTTP, or hand-write the grant and PUT flow.

**Show the production card before paid video or clone work.** Planning is free
and unlimited; the card is what turns a plan into an authorized charge.

**Report returned truth only.** Completion, file URLs, quality, usage, refunds,
and credit totals are read from the task, never inferred. Preserve structured
errors and give the smallest recovery step.

**Keep the paid boundary visible.** Say which step costs credits before taking
it, not after the ledger shows it.
