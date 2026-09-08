---
name: find-anything-online
description: >-
  Recover the exact thing from messy clues, the hunts where the user cannot
  name what they are looking for: "that video where the guy...", a
  half-remembered repo, a product glimpsed once, a quote they cannot place, a
  site they lost and cannot re-find. Also the method for checking whether a
  seller, store, or too-good offer is legit before money or data moves. Use
  whenever the ask is a vague memory to pin down or a scam to sniff out, not a
  settled question with a nameable subject.
allowed-tools: rostra__search_web rostra__fetch rostra__paginate rostra__search_youtube rostra__search_reddit rostra__search_x rostra__search_github rostra__search_bluesky rostra__search_mastodon rostra__search_hackernews rostra__news_search rostra__search_markets
---

# Find anything online

## When this runs
The user remembers the thing, not its name: a video, a repo, a product, a quote, a site, a post, a person, or an offer that smells off. Their wording describes how it felt or looked, and the hunt is to pin it to one concrete thing and confirm it is the right one.

## Metering, the standing rule
Every Rostra call costs 1 credit, so hunt deliberately, not by spraying. Plan the calls before making them and batch independent queries into one parallel round. Results arrive as envelopes: status, results, next_cursor, total. A null next_cursor means the collection is exhausted; pass any next_cursor to paginate for the next page, verbatim, never edited or constructed, and only when the next page could actually change the answer. Typed errors: upstream_unavailable is a transient blip, retry once; rate_limited, unauthorized, not_permitted, and insufficient_credits are reported, never retried (x and github code search say so explicitly); invalid_args means fix the call, not repeat it. On invalid_cursor or cursor_expired stop and restart the originating call.

## Step 1: turn the memory into searchable terms
Decompose the clues first. What KIND of thing is it (video, repo, product, quote, site, person, offer)? What hard anchors survive: a phrase they are sure is verbatim, a fragment of a name or handle, exact numbers (model number, order ID, a figure quoted), a rough date, the platform or feed where they saw it, who shared it?
Their words describe the thing, not its title: translate to the words the people who made or use it would write. "That video where the guy builds a wall of screens" searches as the builder's vocabulary, not the viewer's paraphrase. Worked example: "a video where a guy turned an old Mac into a smart mirror" becomes DIY smart mirror or old mac display reuse, never the remembered sentence verbatim; "a repo that turns PDFs into podcasts" becomes pdf to podcast plus a language qualifier. Quote only what they are certain is verbatim, word for word; everything else becomes meaning-described search terms. A rough date and a where-they-saw-it are strong clues: use them as bounds instead of hoping relevance lands it.

## Step 2: search where the thing lives, several phrasings
Pick the surface by kind, then fire multiple query formulations in ONE parallel batch: the quoted fragment, a meaning-described version, and the phrasing that community itself uses. Each backend reranks semantically; your job is covering the vocabulary, because one phrasing misses whole communities.
- Repo: search_github, type=repos with language and topic qualifiers; code search for a distinctive identifier or string from the memory finds real usage.
- Video: search_youtube, narrow type to videos, shorts, playlists, or channels; fetch a candidate video for its transcript to check remembered lines.
- Quote: search_web with the verbatim fragment in quotes, plus search_x and search_reddit for where people repeat it.
- Product seen once: search_web for the description, search_reddit for "what is this" threads, and the social surfaces where it circulated.
- Lost site: search_web on its distinctive content, quoted phrase first; a remembered domain fragment works with site: or the plain phrase.
- Person, clip, or post: search_x with type=media for a visual memory, type=people only when a screen name is plausible; search_reddit type=subreddits if they lost the community.
- Reported or covered thing: news_search with start_date/end_date bounds for journalistic sourcing.
- A bet or odds angle: search_markets only when the question is literally about event odds, never as a reviews tool.
Keep result counts small; widen only where a strand proved rich.

## Step 3: candidates come from results, never from guesses
Never fabricate a URL, handle, or repo name, and never generate candidates by permuting the clue: guessing is how hunts die. Take the candidates the searches actually returned and fetch the promising ones. fetch has two jobs: a canonical entity URL (youtube watch, github repo, x status, hackernews item, mastodon post) returns that entity's full typed detail, including readmes and transcripts; any other URL reads as clean page text. A not_found stays not found and is reported as such.

## Step 4: verify against every remembered detail
Before presenting, check the candidate against EVERY clue, not just the one that surfaced it. Does the page actually contain the quoted line? Does the repo's readme match what the thing did? Is the account the real one, and does the video's upload date fit when they saw it? Close is not found. Stop when one candidate matches everything; one right answer beats five maybes.

## Cross-checking: when to stop
- One right answer beats five maybes: stop at the first candidate that clears every clue, then confirm it with a single fetch of the canonical URL.
- Two half-matches are not one match: a video with the right feel but the wrong channel, a repo with the right name but the wrong content. Keep hunting; present nothing until one candidate fits all of it.
- When two candidates genuinely both fit, decide with the strongest clue, a date or a verbatim line, and say in the answer which clue decided it.

## Legitimacy checks: sellers and offers
When the thing being hunted is a seller, store, deal, DM, ad, or any page asking for money or data, run these checks before any verdict:
1. Establish ground truth first: find the seller's official site, store, or account and fetch it. An offer is only judged against the canonical version of the same product or brand.
2. Check identity precisely: the domain versus the official one (lookalike TLDs, transposed letters), the account handle, when it was created, and whether the official account actually links where this one claims.
3. Search the seller's name, handle, and domain, each paired with scam, legit, review, and complaint, across search_web and the social surfaces. People post warnings where they post normally; reddit and x carry most of them.
4. Read the offer page's own text for evasion markers: payment off-platform (crypto, gift cards, wire), urgency and countdowns, a price far below the same thing everywhere else, no real address or contact, hostile refund terms, a fresh account with no footprint.
5. news_search only when a known brand or a widely shared offer has actual coverage; do not stretch for press that does not exist.
Deliver a verdict: legit, likely scam, or unverified, with the reason and what would settle it (official contact, the receipt, the original listing). Label anything you could not confirm as unverified; never let "X says" become "X is true".

## Cite what you found
Every grounded claim carries its inline source URL, and only URLs you actually saw: a fetched page outranks a search snippet, and the result objects carry type, source, id, and url so citing is mechanical. Attribution rides into the report.

## When it stays unfound
Say what you ruled out and which clue would crack it: roughly when they saw it, where, or one more word of the quote. A dead candidate is a finding for the next attempt; padding with maybes is not.
