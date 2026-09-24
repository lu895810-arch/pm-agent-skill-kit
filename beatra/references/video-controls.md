# Video controls

Use this reference after selecting one video action. Public controls are model-aware. Call
`beatra.models.list` with the selected capability instead of guessing supported models,
defaults, input limits, or prices. Copy the matching payload from
[videos](videos.md). Returned control names are exact MCP request paths;
dotted names are nested objects and `[]` addresses each item in an array.

## Model selection and defaults

Omit `model`, or use `auto`, when the user does not require one. Auto evaluates live models
in priority order and selects the first model that satisfies the complete request. Pass an
explicitly requested model unchanged; if it is incompatible, report the rejection and offer
compatible choices from discovery.

Omitted controls use the selected model's declared defaults. There is no global default
shared by every video model. Read `defaults` from discovery for the selected
capability; it is the source of truth for resolution, duration, audio, watermark,
search, and last-frame behavior.

`defaults` is not the source of truth for aspect ratio. A model publishes a default
aspect ratio whether or not the selected capability honours one, and where the model
derives the output shape from the input media that published value is never applied —
echoing it back is rejected rather than ignored. Decide aspect ratio from what the card
advertises for that capability, never from `defaults`.

Read the admitted task input and `resolved_model` as the concrete truth after auto
selection.

## Output controls

`resolution` selects a model-defined output tier, not a literal width and height. Discover
the allowed resolution tiers, aspect ratios, and duration values for the selected capability.
Returned width and height are factual result metadata and may differ from the tier label.
Some models accept `duration: "auto"`; when they do, the model chooses a duration within
its advertised range and the actual final output duration determines billing. Do not send
`duration_seconds` as an input field: that name appears in discovery SKU data, usage, and
output artifact metadata, while billable video tools accept `duration`.

Only send optional controls such as `watermark`, `generate_audio`, `web_search`,
`return_last_frame`, `seed`, `negative_prompt`, or `enhance_prompt` when discovery lists
them. Unsupported controls are rejected rather than ignored.

`adaptive` lets the model or input media choose the closest supported aspect ratio. For a
strict output ratio, pass an explicit ratio. When first and last frame images have different
ratios, the first frame is authoritative and the last frame may be center-cropped to fit.

`return_last_frame: true` asks for a separate image artifact whose dimensions match the
output video. Read it from the completed task's own `last_frame` result rather than from the
convenience artifact list, which does not carry it. To create a longer continuous sequence, use that returned image as the next
`animate` request's input; this is a continuity technique, not video extension.

## Media values

Every media value is one of:

```json
{ "type": "artifact", "artifact_id": "art_..." }
```

```json
{ "type": "url", "url": "https://example.com/input.mp4" }
```

```json
{ "type": "data_uri", "data": "data:image/png;base64,..." }
```

Use uploaded artifact IDs for local files; never send filesystem paths. A `data_uri` must
fit the published inline limit. Public URLs must be direct HTTPS objects reachable without
redirects to private addresses.

Use only the current per-kind, per-item, aggregate, duration, combination, and
role limits returned by discovery. Treat every returned maximum and combination
rule as hard even if another execution route might accept more media. Never
truncate, merge, or drop a reference, and never synthesize a charge for an input
kind whose returned price rows declare it free.

A five-image limit is binding only when the current returned interface card
actually reports that value; it is an example of how to apply live discovery,
not a remembered cap.

Use `references` items shaped as `{ "kind": "image|video|audio", "media": ... }`.
Prompt references are numbered from one within each media kind and preserve submitted order.
Set `role` only when model discovery advertises semantic roles. Set a voice reference at
the exact `references[].reference_voice` path only when discovery advertises that control.

Operation-specific slots:

- `generate`: required `prompt`, optional `audio` when advertised.
- `animate`: required `image`, optional `prompt` and `driving_audio`.
- `enhance_prompt`: required `prompt`, `duration`, and `aspect_ratio`; optional
  strict frames or ordered image, video, and audio references. It returns text,
  not video, and ignores its compatibility-only `model` input.
- `interpolate`: required `last_frame`, optional `first_frame`, `prompt`, and
  `driving_audio`. A last-frame-only request requires a compatible model card.
- `generate_from_references`: required `references`, optional `prompt`; it has no strict
  `first_frame` field.
- `edit`: required `source_video` and `instruction`, optional multimodal `references` and
  `audio_setting`.
- `extend`: required `video`, `direction`, `duration`, and `instruction`, plus optional
  image and audio `references`. Direction is `before` or `after`; extension references
  cannot contain additional videos.

For editing and extension, `duration` is the target final output duration. It is not an
instruction to splice locally or add an exact number of seconds. `audio_setting` controls
how supported edit models handle audio.

## Estimate customer credits

Every returned video price option includes a `billable_quantity` object. Read its `basis`
and `counted_inputs`, then apply
`(unit_price_credits * billable_quantity) / scale`. Output pricing normally uses admitted
output duration; extension uses the requested final output duration. Input pricing can use
source-video seconds, reference-video seconds, or both.

When discovery returns separate input-video and output-video price rows, add
both components. Do not synthesize charges for free images or audio.

For `capped_reference_video_seconds`, calculate each referenced video's counted seconds
with the returned `per_video_cap_seconds_by_video_count` map and respect the returned
aggregate maximum. Do not substitute remembered caps. The terminal task's usage and billing
remain the final truth.

## Recover from admission errors

- A concrete-model `unsupported_option` is non-retryable without changing arguments.
  `error.param` identifies the field. In `details.candidate_failures[]`, inspect the
  specific `code`: `unsupported_resolution`, `unsupported_duration`,
  `unsupported_aspect_ratio`, or `unsupported_control`, plus `received` and
  `supported_values` when present.
- `no_eligible_model` means no live auto candidate can satisfy the full request. Inspect
  every provider-neutral candidate failure before relaxing a requirement.
- `model_unavailable` can mean the named model supports the request but no compatible live
  route is currently ready. It is retryable; do not weaken explicit parameters silently.
- A schema-level `invalid_request` means the payload shape itself is invalid, such as an
  additional video inside extension `references` or `duration: "auto"` on extension.

MCP errors use `isError: true` and carry the complete public error in
`structuredContent.error`. Preserve that object so an agent can correct only the rejected
field and submit a new logical request with a new `client_request_id`.
