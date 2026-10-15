# Coding Assignment 1: Contribution and commitment

The user approved these three features on 15 October 2026, prioritizing simple
implementation and clear explanations. They appear together on the signed-in
home feed and reuse the existing SQLite posts, comments, and users tables.

## Features and Design Claims

1. **Chapter 2, Claim 1: visible contribution opportunities.** Show the five newest
   posts by other users with no comments, with a short preview and a Reply link.
   Any comment removes a post from this list. The list is independent of the
   main feed's pagination and filters and has an explicit empty state.
2. **Chapter 2, Claim 15: feedback about goal progress.** Set a weekly goal of
   commenting on three distinct posts by other users. Count existing comments
   created this week, exclude comments on the user's own posts, and count repeat
   comments on the same post once. Show dates, a progress bar, and completion
   feedback. Progress updates on each page load and after posting a comment.
3. **Chapter 3, Claim 30: show received community support.** Count other members
   and their comments on the user's posts this week. Link to the three latest
   comments and provide a Help someone else link to the unanswered-post list.
   Exclude self-comments and show an honest empty state when no comments arrived.
   Comments indicate participation, not a guarantee that every reply is helpful.

The goal counts posts, not necessarily three different authors. Deleting a
qualifying comment or post removes its contribution from progress. Counts may
exceed three, but the progress bar stops at 100 percent. Weeks run from Monday
00:00 to the next Monday 00:00 in Europe/Helsinki, with SQLite's UTC timestamps
converted at query boundaries. Received support uses comment time, not post time.

## Implementation

- A small `contribution.py` module calculates week boundaries and issues bounded,
  parameterized queries against the request's existing database connection.
- `app.py` loads dashboard data only for the authenticated session's user ID,
  moderates previews using the existing function, and passes data to the feed.
- A Jinja partial provides accessible progress, concise text, links, and empty
  states within the existing Bootstrap styling. Comment anchors support links
  directly to a response on the post detail page.
- No schema migration, scheduler, separate counter, or new dependency is needed.

## Validation and delivery

Use temporary SQLite fixtures to test week boundaries (including daylight saving),
duplicate replies, self-comments, completion, empty states, and session isolation.
Use Flask's test client to submit a reply and verify that the opportunity disappears
and both accounts' summaries update. Check the browser layout and reply journey
at desktop and mobile widths. Keep the provided database unchanged during tests.
Document setup, feature behavior, claim sources, and a short demonstration script
in the repository, then commit and push the tested implementation to the fork.

## Claim sources

These descriptions paraphrase the authors' chapter drafts. Check exact wording
against the assigned course book when writing the report.

- https://kraut.hciresearch.info/wp-content/uploads/2020/02/Kraut10-Contribution-current.pdf
- https://kraut.hciresearch.info/wp-content/uploads/2020/02/Ren10-Commitment-current.pdf
