---
name: person-research
description: >-
  Research who a person, company, project, organisation or product actually
  is. Use for "who is X", "what do we know about them", due diligence before
  messaging, meeting, hiring, buying from, partnering with or investing in
  someone, and for "is this site, seller, or offer legit" checks. Identity and
  aliases come first, then official sites and primary accounts, then current
  role and status against stale mentions, then what they say, make, and what
  others say, with verified facts kept apart from inference and reputation.
  Dispatch deliberately: resolve before you search and finish in a
  structured brief.
allowed-tools: rostra__search_web rostra__search_x rostra__search_reddit rostra__search_youtube rostra__search_github rostra__search_hackernews rostra__search_mastodon rostra__search_bluesky rostra__news_search rostra__fetch rostra__paginate
---

# Person research

Build a reliable picture of who a person, company, project, organisation, or product really is: the identity behind the name, what they claim, what they have done, what others say, and what is current. The same method serves a "who are they" brief and an "is this seller legit" check. Everything here is read-only, so the work is planning, not spraying.

## Standing rules
- Dispatch deliberately.
Plan the calls before making them, keep per-call result counts small, batch related queries into one round, and paginate only when the next page could change the answer. Never spray queries to see what sticks.
- Read the envelopes: transient upstream blips (upstream_unavailable) get one retry; policy errors (unauthorized, not_permitted, rate_limited, insufficient_credits) are reported verbatim, never retried; invalid_args means fix the call, not repeat it.
- Every kept claim carries its inline source URL, and only what you actually saw is cited. Never fabricate a URL, handle, title, or quote; a not_found stays not found and is reported as such.

## Phase 1: fix the identity before any search
- Write down the exact subject and its aliases: full name, screen names, handles, domains, trading names, product versus parent company. Decide what kind of thing the subject is first: a person, company, project, and product that share a name are different subjects.
- If the host offers a memory tool, check it first: this may be someone already known, met, or researched; treating a known person as a stranger wastes credits.
- Collisions are the norm, not the edge case. Same-name evidence never merges into one person; unresolved, it stays two candidates and you say so.
- Never research an ambiguous name. Get one confirmed anchor (their own site, a verified account, an employer page, a repo owner) before attributing anything to the subject.

## Phase 2: canonical anchors, official sites, primary accounts
- rostra__search_web to find the entity's own surfaces, then rostra__fetch the canonical URLs: a github owner/repo returns typed detail with its readme, an x status, hackernews item, youtube watch, or mastodon post returns its full typed record, and any other URL reads as clean page text.
- Resolve accounts on each platform with its native people search, never a keyword search of the name:
  - X: rostra__search_x type=people. Results surface screen names, not bare numeric ids; take the handle as the anchor and later scope posts with from:<handle>.
  - YouTube type=channels for their channel; GitHub type=users for their login (a name as a repo or code query is pure noise; resolve the user first); Reddit type=users; Bluesky profiles; Mastodon profiles.
- For an organisation or product add: official site, repo and readme, jobs page, changelog, filings. Official handles cross-link to each other and to the site; a verified badge on one platform proves nothing about the others.
- Sort official from fan pages, lookalikes, and impersonators before treating anything as primary. "Official" is a claim the evidence must support, not a label to inherit from search rank.

## Phase 3: current role and status, date-checked
- Establish the CURRENT role, title, employment, or project state early, because stale mentions are the loudest noise. A 2021 title is what they were in 2021, not what they are.
- Date-check everything kept: set date bounds by default (since:/until: on x; start_date/end_date on news_search, reddit, hackernews, bluesky). rostra__news_search for journalistic coverage of role changes, departures, funding, launches, outages.
- Prefer the subject's own most recent dated words over third-party summaries of them. When the newest primary trace is old, report "latest trace is <date>" instead of guessing at the present.

## Phase 4: widen in order, keep the three tiers separate
- Widen from the anchor in this order: their own words (posts, talks, commits), what they made (repos, products, shipped work), others' words (coverage, mentions), then crowd takes. Fetch the pages that are the evidence instead of trusting snippets.
- Timeline: search x with from:<handle> and dates to bound it. What they shipped: fetch their github user and read repos sorted by stars or updated. Their channel's own uploads are them talking; interviews and coverage are others' words about them.
- Tag every kept fact with WHO said it. A stranger's claim about the subject stays a claim; the source is never the subject. "X says" is not "X is true", and the attribution rides into the brief.
- A post is a dated utterance, not a timeless belief. Never infer private traits from thin public traces.
- Hold three tiers apart in your head and in the brief: verified facts (primary, dated, confirmed), inference (labelled as inference), and reputation (what people say, tagged with who said it).

## Phase 5: the structured brief
Deliver a brief, not a dump:
- Identity: canonical name, aliases, handles, official site, primary accounts, and what kind of thing the subject is.
- History: the dated arc and what they made or did, with inline source URLs.
- Relationships: employer, team, partners, notable connections, as far as the sources actually go.
- Recent activity: the newest dated traces on each surface.
- Open questions: what could not be verified, what is stale, and which collisions stayed unresolved.
End with the gaps named. Found is not the same as worth repeating: old embarrassments, doxxy detail, and speculation stay out of the brief unless they were asked for directly.

## Pointed at an offer, site, or seller ("is this legit?")
Skepticism is the whole method: verify the entity BEHIND the page (who runs this, do they exist beyond it), search "<name> scam" and "<name> reviews" verbatim, weigh track-record age against too-good pricing, and check whether the praise traces to independent people or to the thing itself. "I can't find anyone real behind this" is a complete answer, and usually the important one.
