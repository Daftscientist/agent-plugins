---
name: video-digest
description: "Turn video into usable knowledge, whether it is a single talk, a tutorial, a review, a course, a playlist, or a whole channel: what the video claims, what to actually do with it, and whether it still applies today. Use for \"watch this for me\", \"summarize this video\", \"is this tutorial worth it\", \"is this still current\", \"check out this youtuber\", \"review this channel\", or \"turn this playlist into a course path\". Also find a specific video or a youtuber and check them out before recommending."
allowed-tools:
  - rostra__search_youtube
  - rostra__trending_youtube
  - rostra__fetch
  - rostra__paginate
  - rostra__search_web
  - rostra__search_reddit
  - rostra__search_x
  - rostra__search_hackernews
  - rostra__news_search
---

# Video digest

One video, one tutorial, one review, a playlist as a course, or a whole channel:
reduce it to what it claims, what you would actually do, and whether it still
applies. Fetch on a YouTube watch URL returns the video's typed detail, and the
transcript comes through fetch's own args. The transcript is the content; the
comments are the reception. They are different data. Creators claim, commenters
report ("broke at step 4", "does not work on v3"), and repeated reports outrank
a confident voiceover.

## When to use

Triggers: "watch this for me", "summarize this talk", "is this tutorial worth
it", "is this course still current", "check out this youtuber", "what did this
review conclude", "what is trending on YouTube right now". If the ask is only
"What is on YouTube about X", search_youtube alone suffices; bring in the rest
of the workflow when judgment about the content is required.

## One video

1. Get the video and its transcript. fetch on the watch URL
   (youtube.com/watch?v= or youtu.be) and typed detail comes back: title,
   channel, publish date, stats, description. Pass transcript=true to include
   the caption track; pass lang= to override the language for non-English
   videos. Pass comments=0 when only the content matters, comments=50 when
   reception is the question.
2. Note the publish date and weigh it against the topic's clock. A CSS-layout
   talk ages slower than one on an AI SDK or a framework. Read the description
   for linked repos, docs, or shownotes; those carry version hints.
3. Summarise the claims, labelled as claims. Say what the video asserts, what
   it demonstrates, and what it only gestures at. Never present transcript
   content as verified fact.
4. Extract the actionable steps as commands, settings, or purchase decisions,
   kept verbatim where exactness matters.
5. Check against current reality. search_web for the repo, docs, or product
   the video names; news_search when the topic moves fast. Compare the video's
   version or landscape with today's before repeating any step.
6. Check reception. Video comments are the first errata layer: repeated
   corrections and "this broke" reports outrank the claims. Then widen:
   search_reddit on the channel, topic, or video title; search_x for the same;
   search_hackernews when it is a tech talk, tool, or launch. One angry
   comment is one person; a pattern across threads is a signal.
7. Deliver claims, then steps, then a freshness verdict, then reception, and
   cite the video URL. If it is a tutorial whose version or landscape has
   moved, flag it as outdated and say what changed since.

## A channel or a youtuber

To vet a channel, first pin the right one with search_youtube type=channels,
then sample, never binge: the few latest uploads plus the few most-viewed tell
you themes, trajectory, and quality. Note that fetch resolves only video URLs
to typed entities today; a channel or playlist URL reads as a page of
markdown, so enumerate content with search_youtube type=videos or
type=playlists instead. Judge reception on recent uploads versus the peak via
reddit and x. When the human behind the channel matters, person-research
carries that judgment; the videos alone do not tell you who they are.

## A playlist as a course

Search or fetch the playlist, digest per-video with the transcript, then order
by dependency, not upload date. Name the redundant entries and produce the
shortest path through it. Condensing is the value; completeness is not.

## Trending

trending_youtube takes no query and returns what is hot right now, scoped by
user_loc. Use it for pulse questions ("what is everyone watching") and as a
discovery entry point, then switch to the single-video workflow on anything
worth digesting.

## Deliberate calls and errors

Dispatch deliberately: one fetch with transcript and comments beats
several bare fetches. Paginate only when the first page genuinely lacks what
you need; cursors are opaque, copy them verbatim, and on invalid_cursor or
cursor_expired restart the originating call. Retry transient blips
(upstream_unavailable, internal_error) once; on rate_limited or
insufficient_credits stop and report rather than hammer. not_found means the
video is gone or the id is wrong; there is no silent fallback.

## Done when

You hand back what it says, what to actually do (version-checked), what the
audience corrected, and whether it is worth their time, in that order, with
the video URL cited. Size the digest to the ask: a two-hour talk's digest is
not a two-page essay unless they asked for depth.
