# Coding Assignment 3 recommendations and newcomers

Code: https://github.com/yyy-tom/mini_social_exercise/tree/assignment-3

This independent branch starts from the original course code on `main`.
Assignments 1 and 2 remain available on their own branches. Assignment 3 adds
recommendations and two newcomer features; it does not include Assignment 2's
moderation implementation or Assignment 1's dashboard.

## What to demonstrate

1. **Recommended tab:** content-based ranking using TF-IDF cosine similarity
   to posts positively reacted to, plus a 0.35 bonus for a followed author.
   Positive means like, love, laugh, legacy haha, and wow. The latest reaction
   is used if legacy data has duplicate rows. Sad/angry do not build interests.
   Own posts and already-reacted posts are excluded. Select the five strongest
   candidates, then display that chosen set newest first, with ID as a stable
   tie break. Explanations identify similarity, followed authors or recent-post
   fallback. Following is a strict filter. No misleading pagination is shown.
2. **Introductions — Chapter 5 Claim 19:** an optional public introduction hub,
   offered after signup and linked from navigation/home. Introductions are
   real posts, marked in the feed and post detail. Other members can use Say
   hello to open the comments and begin a conversation. A member can have one
   active introduction; repeated or concurrent submissions reuse it. Deleting
   that post allows a fresh introduction. No age restriction prevents an
   established member from introducing themselves or helping someone else.
3. **Private practice — Chapter 5 Claim 24:** a sandbox for a practice post,
   reaction and reply, with a three-step indicator and reset. These forms do
   not write posts/comments/reactions, train recommendations or store practice
   text in session cookies. State exists only in the current page and escaped
   form fields; opening /practice again resets it. Publication is a separate,
   deliberate action in the real introduction hub or feed.

## Run the demo

From the repository root, with Python 3.11 and the original requirements:

```sh
.venv/bin/python tools/create_assignment3_demo.py
MINISOCIAL_DATABASE=.local-data/assignment3.sqlite .venv/bin/python app.py
```

Open http://127.0.0.1:8080/. Demo accounts: `demo_alice`, `demo_bob`,
`demo_carol`, `demo_dave`. All use `demo-password`.

Alice starts with no introduction, reactions or follows. Her initial
recommendations are recent film posts. Like Bob's DIY post at `/posts/1`, then
follow him at `/u/demo_bob`. Recommended selects DIY posts 2–6, displayed in
reverse chronological order. Following shows the eligible posts by Bob only.
Dave already has an introduction in the hub. Use Alice to practise, then
introduce herself; use Bob to reply and welcome her.

The generator never overwrites a file. For another take, pass e.g.
`--output .local-data/assignment3-take2.sqlite`, and select that same file when
starting the app. The supplied database.sqlite is unchanged during development.
On a selected runtime database, first connection adds the introductions metadata
table automatically; it leaves the existing table definitions alone.

Set a private `MINISOCIAL_SECRET_KEY` if you need sessions to survive server
restarts; otherwise a fresh signing key is generated per process.

## Verification and limitations

```sh
.venv/bin/python -m unittest discover -s tests -v
```

32 tests use disposable SQLite databases. They cover ranking and display order,
positive/negative/legacy reactions, anonymous and Following behavior, cold start,
current activity changes, duplicate signals, bounded read queries, authentication,
HTML escaping, introduction ownership, duplicate/concurrent submissions,
transaction rollback, deletion/recreation, real welcoming replies, signup
navigation, practice isolation and reset. A separate check on a disposable copy
of the course dataset uses the provided DIY example posts and followed users;
it returns five new posts by starboy99, DancingDolphin and blogger_bob.

The recommender is deterministic and designed for this small dataset. It uses
word overlap, so it cannot infer synonyms, understand intent or guarantee a
member will like a post. Wow is treated as a positive signal even though it can
sometimes express surprise. Computing vectors over all posts on each request
is acceptable for the course dataset; larger communities would need caching or
an indexed recommendation service. None of these features demonstrates a
measured improvement in retention or learning without a user study.

## Submission

The [report draft](assignment-3-report.md) has 458 words including all five
questions and the public branch link. Review the personal reflections and AI
disclosure, then paste the report into Moodle's text editor. The
[demo script](assignment-3-demo-script.md) fits a two-minute recording.
An annotated 87-second video is supplied at
`coding assignment/3/Assignment 3 demo.mp4` in the course folder.
Review it, or record your own version, before uploading the video and report to
**Coding assignment 3 return box**. Deadline: **30 October 2026**.

## Design sources

Chapter 5, *The Challenges of Dealing with Newcomers*, Claims 19 and 24.
The [author-hosted chapter draft](https://kraut.hciresearch.info/wp-content/uploads/2020/02/kraut10-Newcomers-current.pdf)
describes public introductions on p.25 and sandboxes on p.33. Lecture 6,
slides 27–31, uses these same claim numbers. The features support the proposed
mechanisms: a basis for conversation and an isolated place to learn by doing.
