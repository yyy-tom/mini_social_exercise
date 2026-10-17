# Assignment 3 recommendations and newcomers

The user approved introductions and a private practice area on 17 October 2026.
This branch starts from original `main`; Assignments 1 and 2 stay independent.

## Recommendation algorithm

Implement the required `recommend(user_id, filter_following)` entry point in
app.py, delegating computation to a small standard-library module. Use TF-IDF
word vectors and cosine similarity to posts positively reacted to by this
member, plus a 0.35 bonus for authors they follow. Treat like, love, laugh,
legacy haha, and wow as positive; sad and angry do not build interests.
Deduplicate historical post IDs. Exclude own posts and posts already reacted
to. Select the best five, using recency and ID for ties, then display that
selected set newest first as required. Following is a strict author filter.
Cold-start and zero-similarity cases use recent eligible posts, preferring
followed authors when available. Return fewer than five only when fewer
eligible posts exist. Anonymous visitors receive recent posts; anonymous
Following requests yield no posts. Show a short explanation per selection.
Recommended is a single five-post view, without misleading page navigation.

## Claim 19 introduction hub

Chapter 5 Claim 19 proposes public introductions as a basis for conversations
between current members and newcomers. A signed-in /introductions page provides
an optional, guided introduction composer and recent introductions, with links
to reply using existing post comments. An introduction is a real public post,
also visible in the feed and marked as an introduction. Add one metadata table
(user_id primary key, post_id unique) to connect users to their introductions.
Creating the post and metadata is atomic. One active introduction per member;
repeat submissions redirect to the existing post. A deleted introduction can
be created again. Both new and established members can participate; no compulsory
entry task or arbitrary age restriction. Signup leads to the hub, and the feed
links to introductions and practice. No messages to external people are sent.

## Claim 24 private practice area

Chapter 5 Claim 24 proposes sandboxes for learning with less community damage.
An authenticated /practice page lets a member create a practice post, add a reply
and try a positive reaction. Use server-rendered forms, clear PRIVATE labels,
a short progress indicator and a reset link. Carry practice text only through
escaped form fields and the current response, never public tables or session
cookies. GET/reset clears it. Practice cannot publish to the real feed. Real
publication is available separately via the introductions hub or home page.

## Boundaries and verification

Reuse existing Flask/Jinja/Bootstrap patterns; no new package is needed. Keep
recommendation and introduction database helpers in separate modules, with
small routes in app.py. Port .j2 autoescaping, the missing abort import and
request-managed connection cleanup where needed. Fix profile links encountered
in recommendation/introduction flows. Retain Assignment 2 stubs in this independent
branch; moderation is available in assignment-2, outside this task's scope.

Tests use temporary copies of the supplied schema, never the tracked dataset.
Cover positive/negative/legacy reactions, follow-only and anonymous modes,
deduplication, exact-five selection and display order, cold start, SQL query
bounds, introduction ownership, repeat submissions, deletion/recreation,
signup navigation, escaping, authentication and practice isolation/reset.
Use a separate seeded Assignment 3 database for browser testing and the demo.
Deliver a clear guide, a 400–500 word report draft with the five questions and
honest AI disclosure, a two-minute script and an annotated recording if supported.
The user reviews personal reflections and submits materials to Moodle.

## Sources

- Assignments - Social Computing 2026-2027.md in the parent course folder.
- Lecture 6 Regulation (cont.) & Newcomers.pptx, slides 27–31 and 34.
- Author-hosted Chapter 5 draft, Claim 19 (p.25), Claim 24 (p.33):
  https://kraut.hciresearch.info/wp-content/uploads/2020/02/kraut10-Newcomers-current.pdf

Reviewed for scope, missing decisions, contradictions and ambiguous behavior.
