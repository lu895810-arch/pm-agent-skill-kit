# Models

Prefer Beatra's automatic routing. Omit `model`, or leave it as `auto`, unless
the user explicitly names a model or asks to choose, compare, or change models.

When model choice matters, call `beatra.models.list` with the exact generation
capability for the tool you are about to use. Pass one JSON object:

```bash
python3 scripts/mcp_client.py call beatra.models.list
```

```json
{"capability": "text_to_image"}
```

Map the next tool to `capability`:

- `beatra.images.generate` → `text_to_image`
- `beatra.images.transform` → `image_to_image`
- `beatra.images.edit` → `image_edit`
- `beatra.videos.generate` → `text_to_video`
- `beatra.videos.animate` → `image_to_video`
- `beatra.videos.generate_from_references` → `reference_to_video`
- `beatra.videos.interpolate` → `frames_to_video`
- `beatra.videos.edit` → `video_edit`
- `beatra.videos.extend` → `video_extend`
- `beatra.videos.enhance_prompt` → `video_prompt_enhancement`
- `beatra.music.generate` → `text_to_music` or `reference_audio_to_music`
- `beatra.speech.synthesize` → `text_to_speech`
- `beatra.voices.clone` → `voice_clone`
- `beatra.images.understand` → `image_to_text`
- `beatra.videos.understand` → `video_to_text`

Do not call with an empty object, `capability: "image"` / `"video"`, a hyphenated
name such as `voice-clone`, a tool name such as `videos.animate`, or
`capabilities: [...]`. Present only the returned selectable models and use its
current constraints, defaults, supported media combinations, and customer price
inputs. Respect an explicit selection and allow validation to reject an
incompatible combination rather than silently substituting another model.

Every returned control name is an exact MCP request path. A dotted path names a
nested object and `[]` names each item in an array, for example
`references[].reference_voice`. Do not flatten or rename these paths.

For image capabilities, the public input and output limit is four. A concrete
model can expose a lower input maximum in its interface card; explicit requests
must respect that value, while `auto` evaluates the complete request and may
select another eligible model. Never truncate, merge, or drop an image. Image
pricing uses `pricing.options`. Select an option only when all of its
`dimensions` match the admitted request; an empty dimensions object is the
default. A preset canvas exposes its `tier` as the `resolution` dimension. When
target-canvas normalization or request-dependent `auto` leaves multiple
eligible prices, quote the returned range and approve against the maximum
rather than guessing. Apply the card's `estimate_formula`; under
`billing_basis: "successful_image_count"`, source-image count never multiplies
the customer estimate and the task's persisted artifacts and terminal billing
are final truth. Never copy model names, tier names, thresholds, or credit
amounts into the Skill as durable catalog data.

For video capabilities, `auto` selection is request-dependent. Discovery's
`auto.candidate_order` is the live priority order; Beatra evaluates the complete
request against that order and selects the first eligible model. The selected
concrete model is persisted on the Task as `resolved_model`. Do not describe
`auto` as one fixed model. If controls are omitted, each candidate is evaluated
with its own returned defaults.

When the user supplies a concrete model, pass that concrete model unchanged.
Do not continue down `candidate_order` and do not silently replace it when the
request is incompatible or temporarily unavailable.

For text-to-speech, customer pricing is linear per 1,000 weighted characters:
each Han ideograph counts as two and every other character counts as one.
Requests below 1,000 are not rounded to a full block. The customer-facing task
contract remains asynchronous while Beatra performs automatic execution
routing internally. The exact TTS model card's
`constraints.supported_languages` is the source of truth for the
public BCP-47 `language` field; see `speech-and-voices.md` for the
current canonical language codes. Voice cloning is priced once per successful
activated voice, including activation. Read both rates from
`beatra.models.list`; do not reuse remembered model or price data.

For a preflight estimate, use the returned price options for the relevant
candidate or concrete model and state that request-dependent auto selection is
finalized at admission. Image cards use their own `estimate_formula` and
dimension-matched `unit_credits`. Other media may use
`(unit_price_credits * billable_quantity) / scale`. For video, read each price
option's `billable_quantity.basis` and `counted_inputs`; when the basis is
`capped_reference_video_seconds`, apply the returned aggregate maximum and
`per_video_cap_seconds_by_video_count` map. For other media, read the returned
`billing_basis`. This is an estimate until actual task usage is known. The
request-time prepaid debit is therefore an estimate for workflows whose
billable duration depends on accepted media or generated output. On terminal
success, use the task's returned usage and billing as truth:
`charged_credits` includes all debits, `refunded_credits` includes any
unused-estimate refund, and `net_charged_credits` is the final charge.

Do not list model catalogs from memory and do not call model discovery as a
routine prerequisite for generation.
