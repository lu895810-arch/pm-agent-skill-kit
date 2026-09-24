# Planning a multi-medium run

One worked scenario, end to end, showing how a business brief becomes an ordered
plan across media and where each paid boundary falls. The per-medium rules stay
in their own references; this file is about the order of decisions and what to
settle before spending anything.

## The brief

A small brand is launching one product and wants two things: a roughly
15-second vertical clip for social in which the founder introduces the product,
and one square still for the product page. They have a product photograph, a
portrait photograph of the founder, and approved copy for a single line of
narration. There is no budget for a reshoot.

Nothing here is a Beatra call yet. Reading the brief, choosing a route, and
writing the plan are free, and they are where the cost of the run is actually
decided.

## Settle the shape before the first call

Four questions decide everything downstream. Answer them from the conversation
where possible, and ask only where a wrong answer would change the paid payload.

**What are the final deliverables, exactly?** "A promo" is not yet a payload.
Two deliverables in two different shapes — one 9:16 clip and one square still —
is a payload, and the fact that they are two shapes is the single most
consequential thing in this brief. See the next section.

**What real media exists?** A product photograph and a founder portrait change
the routes fundamentally. A spoken-delivery clip built from a real portrait is
the sanctioned recipe; inventing a presenter is not.

**Which media depend on which?** A narrated clip is not one call. The narration
has to exist before the video that carries it, and the video card's admitted
**formats and durations both** constrain what you may synthesize — a format the
speech card offers is not automatically one the video card admits. Dependencies
decide the order, and getting the order wrong means paying twice.

**Where is the user's wording load-bearing?** Approved copy is approved. It goes
into the narration unchanged, and any expansion elsewhere gets disclosed.

## Two destination shapes mean two stills

`beatra.videos.animate` takes a **strict first frame**, not a loose visual
reference: the frame you hand it is the one the clip opens on.

What that frame does to the clip's **shape** is decided per model, and this is
the one place in this run where guessing is expensive: most `image_to_video`
models derive the shape from the frame, while a few take it from the request and
fall back to their own default. Adding `driving_audio` also narrows which models
are eligible at all, so the model that actually runs this request need not be the
one a bare `animate` call would have selected. That is why step 1 reads the card
and step 5 of [video recipes](video-recipes.md) decides `aspect_ratio` from what
it says, instead of either being settled by a rule carried in from another run.
Everything else — admitted duration, resolution, formats, and controls — comes
from the card either way.

That makes this brief two image branches, not one:

- **the 9:16 opening frame**, composed for the vertical destination from the
  founder portrait; and
- **the square page still**, composed from the product photograph.

Reusing one still for both is the single most expensive mistake available here:
either the page gets a vertical image or, far worse, the social clip is animated
from a square frame and comes back the wrong shape after the animate call is
already paid for.

## Order the run by dependency, not by medium

For this brief the order is fixed by what constrains what:

1. **Read the video card first** — `beatra.models.list` with
   `{"capability":"image_to_video"}`. Free. First confirm a current card admits
   an `[image, driving_audio]` combination at all — some image-to-video models
   generate their own audio and accept no custom track, which rules this route
   out before anything is spent. Then read the admitted duration, resolution,
   formats, whatever the card says about output shape, and the audio slot's
   accepted formats, size ceiling, and duration window. Reading this after
   synthesizing narration is the classic way to produce audio that no admitted
   duration or format can carry.
2. **Read the speech card too, and pick a format both accept.** Free. If the
   user asked for a format the video route rejects, say so now, before any paid
   call.
3. **Synthesize the narration** — `beatra.speech.synthesize`, written to fit the
   admitted duration and in the agreed format. Paid, and authorized by the
   direct request. Hand the user the audio with its real duration, MIME type,
   and size, and a chance to reject it before the video stage; a script preview
   is not an audio review. Say plainly when the host cannot play the file, and
   do not block on a review it cannot render.
4. **Compose the 9:16 opening frame** — the founder portrait uploaded through
   the bundled client, then one `beatra.images.transform` to the vertical
   canvas. Paid, and authorized by the direct request.
5. **Compose the square page still** — an independent branch from the product
   photograph, with its own square canvas. Paid, and authorized by the direct
   request.
6. **Animate** — `beatra.videos.animate` with the accepted 9:16 frame as
   `image` and the narration as `driving_audio`, handling `aspect_ratio` the way
   video recipes step 5 says this model requires. Paid, and **not** authorized by the
   direct request: this is where the production card comes first. Note that
   `driving_audio` is truncated to the video's duration and audio shorter than
   the clip leaves silence, which is another reason step 1 precedes step 3.
7. **Deliver** — every artifact, the resolved models, and the actual charges.

Music, if the brand wanted a bed as well, would slot beside step 3 as an
independent branch: it depends on nothing the video decides except total length.

## Where the paid boundary actually falls

Steps 1, 2, and the uploads are free. Steps 3, 4, and 5 are single paid calls
that a direct, well-specified request authorizes once each. Step 6 is the one
that needs the production card — the six fields in the main instructions,
carrying this route's tool name, the live-card duration, resolution and aspect,
and the provisional estimate.

The useful habit is to say this shape out loud before step 3, not before step 6:
the user learns that three small charges are coming and one larger one needs
their go-ahead, while there is still time to drop a deliverable. Discovering the
video gate after the narration and both stills are paid for is a worse
conversation.

## What carries between steps, and what must not

**Carries:** the brand's approved copy, the two destination shapes, the product
and founder must-keeps, the accepted 9:16 frame from step 4 into step 6, and the
narration artifact from step 3 into step 6.

**Does not carry:** a `client_request_id`. Each of steps 3, 4, 5, and 6 is one
logical paid operation with its own stable ID, created only after that step's
payload is final. An identical retry of a step keeps that step's ID and its
exact frozen payload; any accepted change to a paid argument is new work with a
new ID and a new confirmation. Reusing one ID across two different steps is the
error — not minting a new one for work that genuinely changed.

**Also does not carry:** a model, format, or price learned in step 1. Each
route's card is read for that route. The image card, the speech card, and the
video card are three different cards.

## When a step comes back wrong

Take the failure back to the step that owns it rather than restarting the run.
A still whose product drifted is a `beatra.images.edit` on the accepted image,
under a new ID and a new confirmation. Narration that reads badly is a fresh
`beatra.speech.synthesize`; it does not invalidate the video card already read.
An animate call that returns off-brief is reported as an outcome, and the user
decides whether to spend again.

The one failure that does restart the plan is an admitted duration, format, or
output-shape behaviour that changed between reading the card and submitting. Re-read the card and
re-cut the narration; do not stretch a payload to fit an assumption.

## The same shape, other briefs

The dependency rule generalizes. Any run that ends in video with sound reads the
video card first and synthesizes to fit both its duration and its formats. Any
run whose destination has a fixed shape composes the opening frame in that shape
rather than expecting a video route to re-crop it, and checks the card to learn
whether that frame or the model decides the output shape. Any run that starts from real
media uploads before it plans prompts. Any run with more than one paid stage
says the whole cost shape once, early, rather than one charge at a time.

For the request payloads themselves, read [images](images.md),
[videos](videos.md), [video recipes](video-recipes.md), [music](music.md), and
[speech and voices](speech-and-voices.md). For symptoms during a run, read
[questions and anti-patterns](faq.md).
