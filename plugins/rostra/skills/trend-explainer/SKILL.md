---
name: trend-explainer
description: "Explain why something is blowing up: a trending topic, a viral claim, a name suddenly everywhere, 'why is everyone suddenly on about X', and whether the wave is real: confirmed vs speculation vs manufactured hype. Use for 'what is going on with', 'is this actually big or just my feed/circle', 'why is this everywhere', and any wave noticed on one platform that needs testing against the rest."
allowed-tools:
  - rostra__trending_x
  - rostra__trending_reddit
  - rostra__trending_hackernews
  - rostra__trending_bluesky
  - rostra__trending_mastodon
  - rostra__trending_youtube
  - rostra__trending_github
  - rostra__trending_markets
  - rostra__topics_bluesky
  - rostra__search_x
  - rostra__search_reddit
  - rostra__search_web
  - rostra__news_search
  - rostra__news_breaking
  - rostra__fetch
  - rostra__paginate
---

# Trend explainer

Explain a wave: what it is, where it started, who amplified it, whether it is real, and how big it actually is. In the answer, say plainly which parts are confirmed, which are speculation, and which are manufactured.

## Workflow

Remember first. You may already know the backstory, yesterday's round of this story, or things the user has told you about the players. The delta beats a cold retelling.

1. What is the wave. Name the thing precisely from what the user said or from what the feeds show. Pulse the trending surfaces to locate it: rostra__trending_x, rostra__trending_reddit, rostra__trending_hackernews, rostra__trending_bluesky, rostra__trending_mastodon, rostra__trending_youtube, rostra__trending_github. rostra__trending_markets shows what people are betting on right now. rostra__topics_bluesky lists Bluesky's native topic labels; pass topic to drill into one topic's post feed.

2. Where it started. Hunt the origin: the earliest post, announcement, or event, and who started it and when. Go oldest-first: rostra__search_x type=latest (reverse-chronological, never re-sorted) with since: and until: operators walking backwards; rostra__search_reddit with sort=new plus inclusive start_date/end_date bounds; rostra__news_search with date bounds for the first coverage; rostra__search_web for an announcement or changelog. Then rostra__fetch the primary source, the original post, repo, video, or article, and read what it actually says.

3. Who amplified it. Map the reaction across platforms. Are the accounts one cluster that all know each other, or independent communities? Which voices broke it and which picked it up? rostra__fetch on a canonical x.com/status, news.ycombinator.com/item, or mastodon post returns typed detail with counts; rostra__search_x type=people finds the accounts. Journalistic pickup shows up in rostra__news_search, not search_web.

4. Is it real or manufactured. Keep three layers separate and label every claim in the answer:
   - Confirmed: what the primary source or a canonical entity says, verified by rostra__fetch.
   - Speculation: claims with no primary source, secondhand retellings, unnamed-sources reporting, and every will-it-happen question. In a story's first hours most claims are unconfirmed; say so plainly instead of narrating speculation as news.
   - Manufactured: coordinated or bought amplification, astroturf, outrage bait, a manufactured controversy. When the wave is a will-it-happen, check the markets: rostra__trending_markets prices it, and priced odds against a loud narrative is the strongest hype-deflator there is.

5. Bubble check. Are your feeds overstating it? Measure the spread, do not assume it. Test platforms away from where the user saw it: a tweet's hype tested on reddit, hackernews, news, and youtube. Check mainstream crossover: rostra__news_search finds it or it does not. "Loud in one graph neighbourhood, absent everywhere else" is a complete and useful answer; deliver it plainly.

## Platform and audience bias

Each surface has a slant and a reach; name both when you use them.

- X trends are region-scoped (woeid from user_loc); without a region you get a blend. rostra__search_x user_loc changes language only, X has no regional egress, and operators from:, since:, until:, lang:, min_faves: pass through the query.
- Reddit trending is /r/popular hot plus rising posts: broad but US and default-subreddit heavy. Search is reranked by default; an explicit sort (hot/top/new/comments) locks that order and disables rerank.
- Hacker News is front-page weight, developer and startup shaped. GitHub trending is repositories; since=daily catches a fresh dev wave, language scopes it.
- Bluesky trending is a curated "what's hot" feed plus native topics; Mastodon trending posts and link cards skew to the fediverse's own bubbles.
- YouTube trending is region-scoped video, a useful mass-audience lagging indicator.
- Prediction markets react in seconds and are priced, not shouted; use them as the sober read, not the loud one.

## Time and place context

Anchor the wave in when and where. State the start time and region when you can find them, and whether the wave is still climbing or already rolling over. Date bounds on the searches are inclusive YYYY-MM-DD; walking them backwards finds origins. rostra__news_breaking is the freshest, fastest-aging surface on the server: do not cache it client-side and do not present older results as current. Trends are read at the moment of the call; say "as of" with a time when the answer could go stale.

## Citing and labeling

Cite posts and articles inline, with their source URLs, so each claim can be checked. If a post's words matter, fetch it; do not paraphrase it into existence. Label confirmed, speculation, or hype on the claims that carry the answer, and keep the labels visible in the summary, not buried.

## Deliberate calls and errors

Dispatch deliberately: spend deliberately: cap results_num to what you will actually read and do not re-ping the same surface for the same page. When a collection carries a next_cursor, continue with rostra__paginate instead of re-running the call. Cursors are opaque: copy them verbatim, never edit or construct one; next_cursor null means exhausted. On invalid_cursor or cursor_expired, stop and restart the originating call. Errors are typed: retry a transient blip once, then report it. Report search_x rate_limited verbatim and never auto-retry it. unauthorized and not_permitted are connection or key policy: never retry.

## Done when

You can give, in order: what happened, why now, who amplified it, how big it really is across platforms, and what is confirmed versus speculation versus manufactured. If you cannot confirm the core claim, the honest answer is the one carrying the labels, not the one that sounds like news.

## Scars

The trending phrase is rarely the story. Search the thing, not the hashtag. And a thing trending on one platform is a fact about that platform's audience, not about the world; say which one you are reporting.
