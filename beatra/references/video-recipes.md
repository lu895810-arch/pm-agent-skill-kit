# Video recipes

Use current models, constraints, and prices from `beatra.models.list` with the
capability payload for this recipe's tool (see [videos](videos.md)). Admit the
complete payload, write the shortest admitted duration (audio-led and extend
rules unchanged), and show the six-field production card from the main
instructions before creating `client_request_id` or submitting
`beatra.videos.generate`, `beatra.videos.animate`, `beatra.videos.interpolate`,
`beatra.videos.generate_from_references`, `beatra.videos.edit`, or
`beatra.videos.extend`. Carry this route's own facts into it: the tool being
called, and the duration, resolution, and aspect read from the live card beside
the provisional estimate. “Make the clip” is not approval. Example `duration`
and `resolution` values below are placeholders;
replace them with the shortest admitted duration and lowest admitted resolution
unless the user named a higher tier. After confirmation, create one opaque
`client_request_id`, call the selected billable tool exactly once, and poll
with `beatra.tasks.get`.

For local media, use only the dedicated bundled upload command. It validates
the `beatra.assets.upload` grant and completes the upload internally:

```bash
python3 scripts/mcp_client.py upload ./input.png --mime-type image/png
```

The command returns a media reference such as
`{"type":"artifact","artifact_id":"art_..."}`.
Do not replace it with an ordinary raw-tool call, host HTTP, or a hand-written
grant and PUT sequence.

## Generate from text

Call `beatra.videos.generate`:

```json
{
  "prompt": "A slow dolly toward a ceramic cup in warm window light",
  "model": "auto",
  "resolution": "720p",
  "aspect_ratio": "16:9",
  "duration": 6,
  "client_request_id": "vid-text-opaque-1"
}
```

## Animate one opening image

Call `beatra.videos.animate`:

```json
{
  "prompt": "The subject looks toward camera while the camera eases forward",
  "image": { "type": "artifact", "artifact_id": "art_first" },
  "resolution": "720p",
  "client_request_id": "vid-animate-opaque-1"
}
```

Decide `aspect_ratio` by step 5 of the presenter recipe below. The same rule
governs this route, and on this route nothing else protects you from it: it is
the difference between a clip in the opening frame's shape and one in a model's
own default.

Optional controls narrow the field before they do anything else. `duration:
"auto"` and `return_last_frame` are each admitted by only part of the catalogue,
so adding either changes which models `auto` may select, and therefore which
shape rule applies to the request you just changed. Add them only when the live
card lists them for the model you want, and re-read the shape rule when you do.

Add `driving_audio` only when discovery says the selected model supports that input.

## Speak a portrait: presenter and digital-human clips

A talking presenter, spoken delivery, or digital-human clip is not a separate
tool. It is `beatra.videos.animate` with a portrait as `image` and narration as
`driving_audio`, which makes the request audio-led: the audio decides the
duration. Order matters, because the video route constrains the audio you are
about to pay for.

1. Before any paid speech, call `beatra.models.list` with
   `{"capability":"image_to_video"}` and confirm a current card admits
   `[image, driving_audio]`. Compare the portrait's actual MIME type, width and
   height, aspect ratio, byte size, and alpha-channel presence against every
   advertised image constraint. A transparent PNG is a common headshot and a
   common rejection.
2. Pick an output format both cards accept. A format the speech card offers is
   not automatically one the video card admits, so read both before
   synthesizing. If the user asked for a format the video route rejects, say so
   before any paid call and let them choose; never switch it silently. Check
   length before you pay, not after. The driving-audio constraint and the
   admitted video durations are different limits, and the audio one is the
   looser of the two, so a script can be admissible as audio and still have no
   video duration that contains it. Estimate the spoken length of the script and
   confirm the route admits a duration at or above it. If it does not, shorten
   the script or split the delivery before synthesizing. Both free card reads
   are done by this point, so put every conflict they found — format, spoken
   length, and portrait fit — to the user in one message rather than one at a
   time.
3. Synthesize with `beatra.speech.synthesize`, then read the returned audio's
   actual duration, MIME type, and size rather than the requested ones. Hand
   the user the audio with those real facts and a chance to reject it before the
   video stage; a script preview is not an audio review. Say plainly when the
   host cannot play the file, and do not block on a review it cannot render —
   the production card that follows is the user's decision point either way.
4. Re-read the `image_to_video` cards against those real audio facts, and
   re-check the portrait facts against the current card at the same time. The audio
   must clear the live minimum and must fit a duration the route can contain.
   Take the smallest admitted duration at or above the actual speech length so
   no words are cut, and do not pad with silence. A fractional narration can
   leave a short held tail, so disclose it and inspect the ending.
5. Decide `aspect_ratio` from the card, not from a rule. On `image_to_video`,
   most models derive the output shape from the frame and reject an explicit
   `aspect_ratio` outright. A few take the shape from the request instead and
   fall back to their own default when it is omitted, so a portrait handed to
   one of those comes back in that default rather than in its own shape. The
   card discriminates: when it advertises an `aspect_ratios` list, that model
   decides the shape and you must say what you want; when it advertises no such
   list, omit `aspect_ratio` and the frame governs. For a strict output shape on
   a listing model, pass an explicit supported ratio — read
   [video controls](video-controls.md) for what `adaptive` does and does not
   promise before reaching for it — and read the returned `videos[].width` and
   `videos[].height` back rather than assuming them; both are best-effort, so a
   missing value is unknown rather than a failure. Do not read a published default aspect ratio as evidence
   of either behaviour; models that ignore it publish one too. When the
   destination needs a shape the frame does not have, obtain a first frame
   already composed for it.

Call `beatra.videos.animate`:

```json
{
  "image": { "type": "artifact", "artifact_id": "art_portrait" },
  "driving_audio": { "type": "artifact", "artifact_id": "art_speech" },
  "prompt": "A restrained presenter delivery with steady eye line and a stable camera",
  "duration": 8,
  "client_request_id": "vid-presenter-opaque-1"
}
```

Approved narration does not authorize the video call, and replacing the
narration is new paid work with fresh audio, a fresh production card, and a new
`client_request_id`. Treat identity, clothing, and background as must-keeps and
review the result for drift instead of promising exact preservation or perfect
lip sync.

## Generate toward a required last frame

Call `beatra.videos.interpolate`:

```json
{
  "prompt": "The product rises and rotates smoothly between the two views",
  "first_frame": { "type": "artifact", "artifact_id": "art_start" },
  "last_frame": { "type": "artifact", "artifact_id": "art_end" },
  "resolution": "720p",
  "duration": 6,
  "client_request_id": "vid-frames-opaque-1"
}
```

`last_frame` is required. Omit `first_frame` when the selected live model card
admits last-frame-only generation.

## Generate from multimodal references

Call `beatra.videos.generate_from_references`:

```json
{
  "prompt": "Video 1 presents Image 1 in a bright studio while preserving the music rhythm",
  "references": [
    {
      "kind": "image",
      "media": { "type": "artifact", "artifact_id": "art_product" }
    },
    {
      "kind": "video",
      "media": { "type": "artifact", "artifact_id": "art_presenter_video" }
    },
    {
      "kind": "audio",
      "media": { "type": "artifact", "artifact_id": "art_music" }
    }
  ],
  "resolution": "720p",
  "aspect_ratio": "adaptive",
  "duration": 6,
  "client_request_id": "vid-refs-opaque-1"
}
```

Use `animate` instead if one image must be the exact opening frame.

## Edit an existing clip

Call `beatra.videos.edit`:

```json
{
  "source_video": { "type": "artifact", "artifact_id": "art_source_video" },
  "instruction": "Replace the cup with the blue bottle in Image 1 and keep the camera move",
  "references": [
    {
      "kind": "image",
      "media": { "type": "artifact", "artifact_id": "art_blue_bottle" }
    }
  ],
  "model": "auto",
  "resolution": "1080p",
  "duration": 8,
  "client_request_id": "vid-edit-opaque-1"
}
```

## Extend after one clip

Call `beatra.videos.extend`:

```json
{
  "video": { "type": "artifact", "artifact_id": "art_source_clip" },
  "direction": "after",
  "instruction": "Continue the camera move until the train enters the tunnel",
  "resolution": "720p",
  "duration": 12,
  "client_request_id": "vid-extend-after-opaque-1"
}
```

For footage before one clip, use the same `video` field with `direction: "before"`. Do not use
`last_frame` on extension; strict frame-to-frame generation belongs to `interpolate`.
