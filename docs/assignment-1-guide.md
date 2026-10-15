# Coding Assignment 1: Contribution and commitment

The three features are in **Your community corner**, above the post composer
on the home page when you are logged in.

| Design Claim | Feature | How it supports the claim |
| --- | --- | --- |
| Chapter 2, Claim 1 | Needs a reply | Makes specific contribution opportunities visible by showing five recent posts by other users that have no comments. |
| Chapter 2, Claim 15 | Your weekly goal | Gives frequent progress feedback toward commenting on three distinct posts by other people. |
| Chapter 3, Claim 30 | Support you received | Shows other members' replies to your posts and offers an opportunity to give back. |

The summaries paraphrase the authors' drafts; use the exact wording from your
assigned book in the report:

- [Contribution chapter](https://kraut.hciresearch.info/wp-content/uploads/2020/02/Kraut10-Contribution-current.pdf)
- [Commitment chapter](https://kraut.hciresearch.info/wp-content/uploads/2020/02/Ren10-Commitment-current.pdf)

## Run with the original course data

From the repository root (Python 3.11 or newer):

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:8080 and sign up or log in. The supplied dataset contains
old activity, so new comments are needed to populate this week's summaries.

## Run a separate demonstration dataset

Stop an already running server first. From the repository root, with the
virtual environment activated:

```sh
python tools/create_assignment1_demo.py
MINISOCIAL_DATABASE=.local-data/assignment1.sqlite python app.py
```

This creates a separate, git-ignored database and never changes the supplied
`database.sqlite`. It refuses to overwrite an existing file. For a fresh demo,
choose another filename with `--output` and use that same filename in
`MINISOCIAL_DATABASE`.

Log in as **demo_alice**, **demo_bob**, or **demo_carol**, using password
**demo-password**. These are local demonstration accounts.

## Suggested two-minute recording

1. Log in as demo_alice. Show the three community sections, her 2/3 progress,
   and the comments she received from Bob and Carol.
2. Under Needs a reply, open Bob's post and submit a thoughtful comment. Show
   the goal-complete feedback.
3. Return to the community corner. Show 3/3 progress and that the replied-to post
   has disappeared from Needs a reply.
4. Log out and log in as demo_bob. Show Alice's new reply under Support you
   received. Click its link to jump to the comment, then use Help someone else
   on the home page to find an opportunity to give back.

## Behavior details

- Weeks run Monday–Sunday in Europe/Helsinki. UTC database timestamps are
  converted to the correct week boundaries, including daylight-saving changes.
- Multiple comments on one post count once toward the goal. The same author can
  have several qualifying posts. Self-comments do not count.
- Progress derives from existing comments: removed comments/posts no longer
  contribute. The bar stops at 100 percent, even after more than three posts.
- Received-support counts use the time of the comment, including replies to
  older posts. Self-comments are excluded; only the three newest replies are linked.
- Any comment removes a post from Needs a reply. This list is independent of the
  main feed's New/Popular/Following filters and pagination.
- Both lists have empty states. Comments are visible participation, and are not
  automatically classified as helpful or positive.

## Verification

```sh
python -m unittest discover -s tests -v
```

Tests use temporary databases. They check account isolation, distinct-post
counting, self-comments, week/DST boundaries, completion, empty states, HTML
escaping, and the comment submission flow for both accounts.

The app now enables HTML escaping for its `.html.j2` templates, so user text is
displayed as text. Reply links to removed posts return a 404, and submitting a
comment to a removed post redirects home instead of creating an orphaned comment.

## Submission reminders

Submit the recording and 400–500 words through Moodle. Include the assignment's
questions and this public repository link: https://github.com/yyy-tom/mini_social_exercise.
Explain each feature's connection to its Design Claim. Write your learning and
difficulty reflections from your own experience. Disclose AI assistance with
feature selection, implementation, documentation, and verification accurately.
