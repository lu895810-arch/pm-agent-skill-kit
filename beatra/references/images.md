# Images

Choose one intent before constructing arguments:

1. No source image: use `beatra.images.generate`.
2. Existing images guide a new composition: use `beatra.images.transform`.
3. Preserve a base and change it: use `beatra.images.edit`.

Authenticated Beatra MCP is the image execution contract. Run image tools
through the Skill's bundled `scripts/mcp_client.py` like every other Beatra
tool.

Example payloads below use placeholder prompts, artifact IDs, and canvas
values. Replace them with the admitted request; omit `model` unless the user
named one.

## Generate from text

Use `beatra.images.generate` with no source image. Translate the requested
subject, setting, composition, style, and constraints into one coherent prompt.
Omit `model`, or use `model: "auto"`, unless the user explicitly selects one.

```json
{
  "prompt": "A ceramic cup on a walnut desk in warm window light",
  "count": 1,
  "canvas": { "type": "preset", "tier": "2K", "aspect": "16:9" },
  "client_request_id": "img-generate-opaque-1"
}
```

## Transform ordered references

Use `beatra.images.transform` when one to four ordered input images guide a new
composition. Upload local inputs once and reuse each artifact ID. Describe both
the intended change and the properties that must remain recognizable. A preset
canvas with `aspect: "source"` follows the last image.

```json
{
  "prompt": "Place the product from the first image into the lit studio scene from the second, keeping the label legible",
  "images": [
    { "type": "artifact", "artifact_id": "art_product" },
    { "type": "artifact", "artifact_id": "art_scene" }
  ],
  "canvas": { "type": "preset", "tier": "2K", "aspect": "source" },
  "count": 1,
  "client_request_id": "img-transform-opaque-1"
}
```

`images` is an ordered array of reference objects, never a bare string or a
local path. Each entry is `{"type":"artifact","artifact_id":"..."}` from the
bundled upload command, `{"type":"url","url":"..."}`, or
`{"type":"data_uri","data":"..."}` — note that the data URI key is `data`, not
`data_uri`.

## Edit a base image

Use `beatra.images.edit` with one to four ordered input images when the first
image must remain the base. Later images are optional references. A preset
canvas with `aspect: "source"` follows the first image.

Use `edit_regions` only for bounded edits. Each region is a normalized rectangle
with `image_index`, `x`, `y`, `width`, and `height` from 0 to 1. It must remain
inside its image, and each input accepts at most two regions. Omit regions for a
whole-image edit.

```json
{
  "prompt": "Remove the passer-by on the left and keep everything else unchanged",
  "images": [{ "type": "artifact", "artifact_id": "art_base" }],
  "edit_regions": [
    { "image_index": 0, "x": 0.02, "y": 0.35, "width": 0.22, "height": 0.5 }
  ],
  "client_request_id": "img-edit-opaque-1"
}
```

## Defaults and public limits

- All three tools request one to four outputs; the default `count` is 1.
- Generate and transform default to a 2K 16:9 canvas. Edit defaults to a 2K
  canvas that follows the base image's aspect ratio.
- A preset `tier` is `1K`, `2K`, or `4K`, uppercase. `aspect: "source"` is
  admissible for transform and edit only; generate has no source image and
  rejects it.
- `output_relationship` defaults to `independent` where available.
- An omitted `seed` is random.
- `enhance_prompt` and `reasoning` belong to different image model families, so
  read the selected model's interface card instead of assuming either exists.
  Where the card lists `enhance_prompt`, omitting it or sending null submits the
  prompt as written, and an explicit boolean also constrains model eligibility.
  Where the card lists `reasoning`, omitting it or sending null keeps that
  model's documented default.
- The public limit is still four when a concrete model can expose a lower input
maximum. An explicit incompatible model fails; `auto` may choose an eligible
model. Inputs are never silently dropped or merged.

Treat an explicit model as a compatibility commitment: reject unsupported
input counts or controls instead of changing the request.

When quoting live model, control, canvas, compatibility, or cost, call
`beatra.models.list` for the chosen image tool:

```bash
python3 scripts/mcp_client.py call beatra.models.list
```

```json
{"capability": "text_to_image"}
```

For transform use `{"capability":"image_to_image"}`; for edit use
`{"capability":"image_edit"}`. Copy the matching value from
[models](models.md). The returned interface card is current truth. Do not
invent a control or silently remove one that the chosen model cannot honor.

## Price, submission, and recovery

Image prices are whole credits per successful image. Query
`beatra.models.list` with that same matching capability for the live
`pricing.options`, estimate formula, and billing basis. Match an option only
when every entry in its `dimensions` agrees with the admitted request; an
empty dimensions object is the default option.
For a preset canvas, its tier supplies the `resolution` dimension. If a target
canvas or request-dependent `auto` route does not identify one option uniquely,
do not invent a tier: show the live range and use the highest eligible option as
the approval ceiling. Multiply the selected `unit_credits` only by the requested
output count. Source-image count is not a customer billing multiplier. The
final charge uses the successfully persisted image count, so a partial
multi-output result is not
billed as if every requested image succeeded.

Create one opaque `client_request_id` after the arguments are final and submit
exactly once. Poll the returned task with `beatra.tasks.get`; `queued` and
`running` are not failures. If the create response is lost, make an identical
retry with the same ID. Any changed prompt, image, model, or control needs a new
ID. A follow-up edit is new work even when it reuses an earlier artifact.
