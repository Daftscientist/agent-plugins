---
name: repo-intelligence
description: >-
  Judge an open-source project before you bet on it: a library you are
  thinking of adopting, a dependency to keep or drop, "is X maintained or
  dead", "X vs Y" library choices, migrating from one project to another,
  or due diligence before adopting anything. Use whenever the question is
  whether a repo is healthy, abandoned, risky, or right for the job.
allowed-tools:
  - rostra__search_github
  - rostra__trending_github
  - rostra__fetch
  - rostra__paginate
  - rostra__search_web
  - rostra__search_hackernews
  - rostra__news_search
  - rostra__search_youtube
---
# Repo intelligence

Health is not stars. Finish every judgment with a verdict, the named risk, and the alternative if
the risk bites.

All Rostra calls are read-only and metered at 1 credit each, so think before you spend: one broad
search beats five narrow ones, and paginate only when the verdict actually needs more pages.
Responses are typed envelopes ({"status": "ok", "results": [...], "next_cursor": ...}); a typed
error code (rate_limited, upstream_unavailable, invalid_args, insufficient_credits) with a message
is the tool talking, not a crash. Retry a transient blip once, then report it. Pass next_cursor
verbatim to rostra__paginate; never edit a cursor. Never cache search results across a session:
repos change, and so do their trends.

## Workflow

### 1. Official docs and positioning

Start with rostra__search_web for the project's own site, docs, and README. What does it claim to
be, who is it for, and what is in scope? Then rostra__fetch on the github.com/owner/repo URL for the
typed repo summary and readme. Date-check every tutorial or blog post you lean on: a 2022 how-to
against a current API is a trap, and a stale tutorial is a signal the project stopped attracting
writers.

### 2. Repository activity and release cadence

Release recency and cadence are the pulse: when was the last release, how regular are they, and does
the pace match the project's age? Cross-check commit activity through rostra__search_github
(repositories, sorted by updated) and the repo's own detail. A big open issue count usually means
popular, not neglected; silence from maintainers means neglected. Judge velocity and trend, not raw
numbers, and compare against the cadence the project promises in its docs.

### 3. Maintainers and org backing

Who actually merges? Check the repo owner (individual vs org), the contributor list via search
results, and whether the people named in the docs still appear in recent activity. One individual
maintainer is a bus factor; an org with a history of shipping is a different risk profile than a
drive-by side project. Search the maintainers' names on rostra__search_hackernews and
rostra__search_web if you want their track record.

### 4. Open issues and unresolved technical risk

rostra__search_github over issues, sorted by updated, tells you what is biting people right now.
Weight unresolved issues that touch your use case harder than generic noise: a long-open crash on
the exact platform you need outweighs a hundred feature requests. Read whether maintainers reply,
and treat a maintainer's explicit wontfix as signal, not noise.

### 5. PRs and architectural direction

The PR queue shows where the project is going and whether contributions land. Stale PRs from outside
contributors, a backlog of reviewable work, and rejected architectural proposals all say something
about direction and governance. Read the discussion on the PRs that matter for your use, and note
whether the maintainers merge others' work at all.

### 6. Licence and commercial restrictions

Check the licence file itself, not the badge in the readme. rostra__fetch the repo and read what the
licence actually permits for your use: copyleft vs permissive, patent grants, dual licensing,
contributor licence agreements. If you are embedding the code in a product, this step is the
difference between a green light and a legal review.

### 7. Archived or deprecated status

Look for the archived banner, the deprecation notice in the readme, and the maintainers' own words
on where development moved. An archived repo is a verdict in itself: find the successor
(rostra__search_github will surface forks and the named replacement) and run the health read on that
instead. Active forks of a dead project are where its successor lives; check them before writing the
project off.

### 8. Community adoption vs marketing claims

Stars, trending placement, and a slick readme are marketing. Adoption is evidence:
rostra__search_github type=code for who actually imports or depends on it, rostra__search_hackernews
and rostra__news_search for how people talk about it, rostra__search_youtube for talks and tutorials
that signal real use. rostra__trending_github this week is a pulse, not production readiness.
Downstream dependents are the strongest signal there is.

### 9. Alternatives and migration difficulty

For an X vs Y choice, run the health read on both sides of the comparison, then weigh the verdicts
against the user's situation: what they already run and how much churn they tolerate. For a
migration, the official guide is the start, not the answer; the breakage list and effort estimate
live in the issues, HN threads, and posts from people who actually migrated. Search the old and new
project names together to find those field reports.

## Judgment, not syntax

GitHub search qualifiers (language:, repo:, in:, user:, sort=updated and friends) belong to
rostra__search_github itself and pass straight through the query. This skill owns the judgment:
which surfaces to read, what each finding means, and how the evidence stacks into a verdict. Cite
repos and issues inline, owner/repo and owner/repo#123, so every claim is checkable by the reader.

## Done when

You can state a verdict (adopt, keep, drop, or avoid), the risk behind it (abandonment, breaking-
change churn, one-maintainer bus factor, licence restriction, unresolved bug), and the alternative
if that risk materializes. No verdict without the risk named. Cite the repo or issue that grounds
each call.
