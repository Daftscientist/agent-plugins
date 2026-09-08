---
name: vibe-check
description: |-
  Find what different communities actually think of something: a product, company, tool, decision,
  or take. Use for "what do people think of X", "is X any good", "worth it?", reviews and reception,
  what a market or niche is complaining about, reading backlash to a launch, or mapping the
  communities that make up a niche. The ground is Reddit, Hacker News, X, Bluesky, Mastodon and
  YouTube comments, with news coverage as a separate lens. Everything is read-only and metered, so
  read deliberately.
allowed-tools:
  - rostra__search_x
  - rostra__search_reddit
  - rostra__search_hackernews
  - rostra__search_bluesky
  - rostra__search_mastodon
  - rostra__search_youtube
  - rostra__trending_x
  - rostra__trending_reddit
  - rostra__trending_hackernews
  - rostra__trending_bluesky
  - rostra__trending_mastodon
  - rostra__topics_bluesky
  - rostra__fetch
  - rostra__paginate
  - rostra__search_web
  - rostra__news_search
---

# Vibe check

Reception, reviews, complaints, backlash, and which communities are even having the conversation.
Not a poll, a read.

## Workflow

 1. Pick where THIS thing's people live. Devtools: hackernews plus reddit. Consumer: reddit plus
   youtube reviews and comments. Discourse and launches: x and bluesky. Press framing is separate;
   run rostra__news_search and keep it distinct from community sentiment.
 2. Sample MULTIPLE query formulations per surface; communities do not phrase things like the
   marketing page. Try the name, the category, the complaint shape ("X broken", "X too expensive"),
   and insider shorthand. Compare what each formulation surfaces.
 3. Sample MULTIPLE communities, never one. Scope the same question across several subreddits, then
   HN, then the social take. Each community is different data; r/selfhosted's take and HN's disagree
   often, and that disagreement is information.
 4. FETCH the threads that matter. Sentiment lives in comments, not titles. rostra__fetch the story,
   post, or video carrying the argument, then rostra__paginate comment pages when the thread IS the
   evidence. Read the replies to a contentious top comment, not just the comment.
 5. For launches and live topics, scan the trending side too (rostra__trending_x,
   rostra__trending_reddit, rostra__trending_hackernews, rostra__trending_bluesky,
   rostra__trending_mastodon, rostra__topics_bluesky): it catches what is hot now beyond keywords.
   Check whether those posts are the community's own or a bigger feed's traffic.

## Reading the evidence

- Separate PROMINENT VOICES from REPRESENTATIVE sentiment: a pinned announcement, an influencer
  review, or a viral rant is one loud channel, not consensus. Ask whether ordinary, unrelated
  accounts repeat the claim before calling it the community's view.
- Separate FACTUAL objections from EMOTIONAL reaction: "the API drops hourly", "the license
  changed", "pricing doubled" are checkable; rage and cringe are feeling, not facts. Verify factual
  objections against docs or a second source; never launder an unverified claim because a thread is
  angry.
- Weight praise and complaints that REPEAT INDEPENDENTLY across communities. Recurring complaints
  are the real signal; so is recurring praise (what the thing genuinely does well). A recurring
  misconception is a finding too: the positioning or docs are failing.
- DESCRIBE DISAGREEMENT rather than flattening it. "HN mostly rates it, the pricing thread is
  hostile, maintainers push back" is a report; "mixed reviews" is a shrug. A split is a finding: say
  who is on each side and why.
- NEVER let engagement equal consensus. Retweets, upvotes, view counts measure reach and
  amplification, not agreement. One viral thread is one person's take carried by the feed; say so
  when you cite it.
- Keep the community attached to its take: attribute every claim to the surface you found it on.
  Discount marketing-adjacent superlatives and fresh accounts saying suspiciously aligned things;
  praise that mirrors the ad copy is a flag, not evidence.

## Bias flags to state in the answer

- Selection bias: search results are not a random sample. Say where you looked and where you did
  not.
- Platform audience bias: x and bluesky run loud and personality-driven, HN skews technical, reddit
  is subreddit-fragmented, youtube comments skew to whoever watched. A take loud on one platform can
  be absent everywhere else. Say which audiences you heard.
- Sort and recency shape results: the settled take (top) differs from the current one (latest/new).
  Say which you read.

## Metering and errors

- Every call costs 1 credit. Fetch only threads you will read and page only collections you already
  used; paying for pages you skim is waste. Prefer a few well-chosen threads over a dozen shallow
  ones.
- Retry a transient blip (rate_limited, upstream_unavailable) once, then report it and move on. On
  invalid_cursor or cursor_expired do NOT retry; restart the originating search instead.
- Cursors are opaque: copy next_cursor verbatim into rostra__paginate. Null next_cursor means
  exhausted. Errors are typed (unauthorized, not_permitted, rate_limited, insufficient_credits,
  invalid_args, upstream_unavailable, internal_error); surface the code on failure.

## Cite and quote honestly

- Cite threads INLINE: link the post, story, or video behind every claim, with community and date. A
  vibe read with no citations is unsupported.
- NEVER fabricate quotes. Quote only words you saw in fetched results; otherwise paraphrase and mark
  it as such. "This HN comment says X" is not "the community says X".

## Done when

You can say what people like, what they hate, who is saying it, on which platforms, and how sure you
are: a vibe with attributed quotes, never fake statistics ("HN mostly rates it, the subreddit is
split", not "78% positive"). Name the loudest objection, the recurring praise, the recurring
misconception, and any split. Flag unsampled surfaces.

## Scars

- One loud thread is not the internet's opinion.
- Titles are bait; the argument is in the comments.
- A split is a FINDING: report it, do not average it away.
- "Nobody is talking about this" counts only once the right surfaces actually returned silence.
