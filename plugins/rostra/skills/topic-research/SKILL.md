---
name: topic-research
description: >-
  Deep research on any question worth real investigation: "is that actually
  true", a claim someone is reckoning, products or options to evaluate, events
  or situations to understand, decisions being weighed, "X vs Y", "is this
  still true", "should I build this", "how do I learn X", and will-it-happen
  questions. Multi-source, primary documents first, verification, comparisons,
  and a grounded verdict with inline source URLs on every claim. Also the
  method a dispatched clone follows for any research task. Not for the quick
  fact one search settles: every Rostra call costs a credit, so small questions
  go to cheaper tools first.
allowed-tools: rostra__search_web rostra__news_search rostra__news_breaking rostra__search_x rostra__search_reddit rostra__search_youtube rostra__search_github rostra__search_hackernews rostra__search_mastodon rostra__search_bluesky rostra__search_markets rostra__trending_markets rostra__trending_x rostra__trending_reddit rostra__trending_youtube rostra__trending_hackernews rostra__trending_mastodon rostra__trending_bluesky rostra__trending_github rostra__topics_bluesky rostra__fetch rostra__paginate
---

# Topic research

## When this runs
Any question with real stakes and more than one plausible source: verify a claim someone made, compare products or options, understand an event or situation, test whether something is still true, weigh a decision, judge a will-it-happen question. This is also the method a dispatched clone follows for any research task. Not for single-shot facts: one search on one source settles those without this machinery.

## Metering, the standing rule
Every Rostra call costs 1 credit. Dispatch deliberately: plan the calls before making them, batch related queries into one parallel round, keep per-call result counts small, and paginate only when the next page could actually change the answer. Never spray queries to see what sticks. Results arrive as envelopes with typed errors: upstream blips (upstream_unavailable) get one retry; policy and metering errors (unauthorized, not_permitted, rate_limited, insufficient_credits) are reported, never retried; invalid_args means fix the call, not repeat it.

## Preflight, before any tool
1. Check memory first (the host's memory tool, when offered): this topic may already be researched, ruled on, or narrowed by earlier work. Do not rebuy work you already own.
2. Name the question and what would settle it. Classify it: current event, evergreen, product, claim, or will-it-happen; the class picks your strands.
3. Fix the entity: one confirmed identifier (the site, the repo, the verified handle) before deep research. Never research an ambiguous name; an unresolved entity wastes whole strands.
4. Rewrite the query the way people write it, not the way they asked: "gift for a 42 year old man" finds nothing, "gifts men actually liked" finds gold. Literal user wording is usually the wrong search; choose the vocabulary each community uses.
5. State the working hypothesis you will test, so you can deliberately search against it later.

## Plan strands, pick sources by intent
Lay 2 to 4 weighted strands, thin searches first, and always keep one strand primary:
- PRIMARY: the thing itself, the repo, paper, filing, docs, product page, or talk. Fetch these; they outrank every summary of them. For technical topics search_github (code search finds real usage, not marketing) and fetch the repo for its readme.
- News and coverage: news_search for what journalistic outlets are reporting (start_date/end_date bounds are inclusive), news_breaking for the topic-less "what is happening right now" pulse, search_web for general finding and source discovery, not as a stand-in for news or a provider's native search.
- Reaction and commentary: reddit, hackernews, x, mastodon, bluesky for what people and communities are saying; hackernews comments type reaches the experts' talk, not just headlines; youtube when the topic lives in talks, demos, or walkthroughs.
- Odds: for will-it-happen questions, search_markets for live open markets and their prices; trending_markets when the question is simply what people are betting on.
- Pulse surfaces (the trending_* feeds and topics_bluesky) only when the question is literally "what is hot right now", never as a lazy substitute for a query.

## Run it: parallel, thin, dated
- Fire 2 to 4 differently phrased queries per strand in ONE parallel batch: synonyms ("layoffs"/"job cuts"/"redundancies"), the words each community uses, and other languages when the story is regional (lang on x, user_loc on news). The backend reranks each phrasing semantically; your job is covering the vocabulary, because one phrasing misses whole communities.
- Keep result counts small; widen only where a strand proved rich. Fetch what you find: canonical URLs (github repo, x status, hackernews item, youtube watch, mastodon post) return typed detail including readmes and transcripts; any other URL reads as clean page text. Read the pages that are the evidence.
- Never fabricate a URL, handle, or result; a not_found stays not found and is reported as such.

## Noise control: breaking vs settled
On loud or fast-moving topics the sort and date knobs are the point:
- Breaking: newest-first order (type=latest on x, sort by date), no rerank, tight recent date bounds.
- Settled: relevance ranking and wider, older bounds (top/reranked); popularity floors (min_faves on x) cut the noise.
- Date bounds (since/until on x, start_date/end_date on news, reddit, bluesky, hackernews) by default, not as an afterthought.
- A topic that broke hours ago has thin, error-prone coverage: say so instead of padding the answer with speculation.

## Weigh the evidence
- A fetched page outranks a snippet; a primary document outranks a blog about it; live market prices outrank a pundit's claim about sentiment.
- Ten stories citing one origin are ONE source: independence is what makes multiple sources multiple. Check who they cite.
- Separate the tiers in your thinking and your writeup: primary evidence, reporting, commentary, public reaction. Each claim carries its tier.
- Run one search phrased AGAINST your current answer, always. Contradictions are findings: reconcile them or say they are unreconciled, never smooth them over.
- "X says" is not "X is true": the attribution rides into what you report.

## Modes, the same method pointed differently
- COMPARISON ("X vs Y"): run the strands for each side, then verdict against THEIR criteria; a draw with reasons beats a forced winner.
- FRESHNESS ("is this still true?"): the same method with a date lens: what is the newest primary source, and does it contradict the old one?
- NARRATIVE VS ODDS: on will-it-happen questions, put what people are saying next to what markets price; divergence is the finding.
- IDEA CHECK ("should I build this?"): four strands: the graveyard (who tried it, why it died, what changed since), the pain (are real people complaining), the field (who competes now), and why now. An honest "it exists and it is good" saves months.
- LEARNING PATH ("how do I learn X?"): gather the good material across docs, video, and real examples, prune what community warnings flag, then order it: shortest path first, depth optional, what to skip named.

## Synthesis and verdict
Produce the deliverable, not a dump: the question, the answer or verdict, reasoning in a few tight points, and every grounded claim carrying its inline source URL, citing only what you actually saw. Name what you ruled out (a dead candidate is a finding your future self needs) and label what stays uncertain: unverified, contested, stale, one-sided. End with the verdict stated in full; finishing silently is not finishing.
