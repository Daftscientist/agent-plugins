---
name: investigation
description: "Reconstruct how something actually unfolded and trace claims to their origin: who started it, when, where it first appeared, how it spread and mutated across platforms, what the underlying receipts say, and whether a circulating claim is real, exaggerated, misattributed, or fabricated. Use for 'who started this', 'what actually happened with', 'is this claim real', 'where did this rumour come from', tracing a quote, video, screenshot, or controversy to its first appearance, and fact-checking viral posts with a timeline."
allowed-tools:
  - rostra__search_web
  - rostra__news_search
  - rostra__news_breaking
  - rostra__search_x
  - rostra__search_reddit
  - rostra__search_bluesky
  - rostra__search_mastodon
  - rostra__search_youtube
  - rostra__search_hackernews
  - rostra__fetch
  - rostra__paginate
---

# Investigation

Investigating is not answering a question: you rebuild a sequence of events
with receipts, then judge the claim against them. so work deliberately: think before each query, prefer one
targeted search plus a fetch of the winning result over five scattershot calls,
and only paginate when the first page shows a real lead.

## Keep running state as you go
Three lists grow through the whole job, saved to notes as you work:
- CLAIMS: exact wording of each distinct claim, earliest source found so far,
  current status.
- TIMELINE: timestamped appearances in chronological order, earliest first.
  Sort by time, never by engagement: the loudest version is rarely the earliest.
- EVIDENCE: fetched receipts with URLs. A screenshot repeated a thousand times
  is ONE piece of evidence; name what you ruled out and why.

## Workflow

### 1. Fix the exact claim
Before searching, write the claim word for word as stated, plus who allegedly
did or said what, where, and when. Note the actors' confirmed handles and check
for ambiguity: a claim about "the video" needs its date, venue, and speakers
pinned down or the search will drift. If the claim itself is vague, say so.

### 2. Find the earliest discoverable appearance
Search each platform with inclusive date bounds (start_date/end_date) or
since:/until: operators where supported. On X use type=latest for true
reverse-chronological order. Walk replies and quote-chains: fetch a post, then
follow its threads via paginate until you reach the head of the chain. Keep
going EARLIER until no result predates your earliest hit; that candidate is the
origin. If nothing settles it, state "origin unresolved past <date>" honestly.

### 3. Separate the original from copies
Distinguish the original source from reposts, screenshots, quote-posts, and
commentary. Check handles, timestamps, and media provenance: a screenshot of a
post is not the post, a quote-tweet is not the tweet, a news write-up is not
the underlying statement. Chase the mutation trail, because how the claim
changed between platforms is usually the story: find who first added the
inflammatory framing, the wrong name, the out-of-context statistic.

### 4. Retrieve the underlying material
When the claim points at a document, video, code, filing, or statement, fetch
the canonical URL and read the primary source itself (fetch handles canonical
entities with full detail, transcripts, and comment trees). A claim about a
video should be checked against the video's transcript; a claim about a quote,
against the quote in context. Never judge a primary source from how others
describe it.

### 5. Hunt corrections
Search news and the original platforms for retractions, editor's notes,
corrections, and community notes attached to the viral posts. A correction
later in time does not erase the claim's spread; it belongs on the timeline as
its own entry with the corrected facts stated.

### 6. Verdict per claim
Classify each claim as supported, partially supported, unsupported,
misleading, or unresolved, and for each say what evidence would settle it
(access to the account, the unedited video, the full filing, the other
participant). Do not average disagreeing narratives: name each one, who pushes
it, and what evidence it actually holds.

## Reporting rules
- Cite inline URLs for every factual assertion and every timeline entry.
- Never fabricate: no invented quotes, dates, handles, screenshots, or URLs.
  If a source cannot be retrieved, mark it unverified rather than guessing.
- Report the timeline, the origin (or its unresolved boundary), where and how
  the claim mutated, each narrative with its receipts, and your read on the
  claim with what would settle it.
- On policy errors (unauthorized, not_permitted, insufficient_credits) stop
  and report; on transient blips (rate_limited, upstream_unavailable) retry
  once, never in a tight loop. Copy cursors verbatim when paginating.
