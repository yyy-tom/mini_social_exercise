# Coding Assignment 2: Moderation

Public code: https://github.com/yyy-tom/mini_social_exercise/tree/assignment-2

This branch starts from the original fork. `main` remains the original course
code, and `assignment-1` holds the earlier contribution and commitment work.

## What is implemented

- `moderate_content()` implements every rule on `/rules`. Tier 1 takes priority
  over Tier 2; each returns the prescribed removal message and score 5.0.
  Otherwise every mild-word occurrence and each external URL adds 2.0, with
  masking/removal, and excessive capitalization adds 0.5. Content scores can
  exceed 5. Matching uses escaped, case-insensitive whole terms.
- `user_risk_analysis()` uses `profile + 3*average_posts + average_comments`,
  then the account-age multiplier (1.5 before 7 days, 1.2 before 30 days, 1
  thereafter), capped at 5.0. Missing groups score zero. It uses original text.
  The admin's post/comment multiplier remains 1.5 for accounts under 7 days.
- **Chapter 4, Design Claim 20:** an interactive private review intercepts
  affected submissions before publication. It displays filtered text, the
  triggered rules and a link to `/rules`, alongside an editable draft.
  Check revision, publish the moderated result, or cancel. A changed affected
  draft or a different comment target requires another check.
- Posts and comments have optional manual preview buttons. Signup introduces
  the same review for profile text; it preserves non-secret fields and asks for
  the password again. It never echoes or stores a password in the preview.
- Public feeds, post pages and profiles filter the stored originals. `.j2`
  HTML autoescaping protects both previews and public displays. The admin sees
  escaped original text for review. No schema change is required.

The original course word lists determine which terms match. They are not a
context-aware language model and will miss unlisted abuse or obfuscated text.
URL detection covers http, https, ftp and www forms; bare domain names without
these prefixes are treated as ordinary text. A risk score prioritizes review;
it does not automatically suspend an account.

## Run the separate demo

From the repository root, install the requirements into a Python 3.11 virtual
environment if needed, then:

```sh
.venv/bin/python tools/create_assignment2_demo.py
MINISOCIAL_DATABASE=.local-data/assignment2.sqlite .venv/bin/python app.py
```

Open http://127.0.0.1:8080/. The demo generator never overwrites a file. To
make another demo, choose `--output .local-data/assignment2-take2.sqlite` and
use that same path in `MINISOCIAL_DATABASE` when starting the app. To inspect
the supplied course dataset instead, omit that environment variable.

- Member: `demo_alice` / `demo-password`.
- Other members: `demo_bob`, `demo_carol` / `demo-password`.
- Moderator: `admin` / `admin`, then open `/admin`.
- Initial user risks: Alice 2.0 LOW, Bob 3.0 MEDIUM, Carol 5.0 HIGH.
- Demo post 1 is Bob's clean discussion. Carol's posts demonstrate severe and
  spam removal. Bob's mild comment demonstrates the new-account multiplier.
- Safe course test tokens: `tier1badword`, `tier2badword`, `tier3badword`.

The app uses a random signing key by default. Set `MINISOCIAL_SECRET_KEY` to a
private stable value if keeping login/preview sessions across server restarts
or running multiple processes. Never commit a private key. No extra packages
are needed beyond the original requirements.

## Verification

```sh
.venv/bin/python -m unittest discover -s tests -v
```

33 tests cover tier precedence, exact matching and occurrence counts, URLs,
capitalization boundaries, score capping, averages, UTC age boundaries,
authentication, preview-before-write, changed drafts and targets, signup
password handling, public filtering, HTML escaping and admin scores. Tests use
temporary databases with the course schema. A read-only check of the supplied
dataset matches all nine high-risk users named in Exercise 5, including the
correct RedRose account (the dataset has two accounts with that username).

Browser verification covers the real posting/revision flow, comment preview,
profile signup review, admin scores, and a narrow mobile viewport. The supplied
`database.sqlite` is unchanged.

## Submission materials

- [Report draft](assignment-2-report.md): 478 words including the required
  questions and GitHub link. Review the learning/difficulty reflections and
  keep the AI disclosure accurate. Paste the report into Moodle's text editor.
- An 81-second silent annotated recording is saved in the course
  folder at `coding assignment/2/Assignment 2 demo.mp4`. Review it before
  submitting. The [demo script](assignment-2-demo-script.md) is available if
  you prefer to record your own version.
- Submit the report and recording to **Coding assignment 2 return box** by
  **30 October 2026**. The code is on the public `assignment-2` branch.

## Design source

Kiesler, Kraut, Resnick and Kittur, *Regulating Behavior in Online Communities*,
Chapter 4, Design Claim 20: reminders at the point of a potentially
norm-breaking action can reduce offenses. See the
[author-hosted chapter draft, p.21](https://kraut.hciresearch.info/wp-content/uploads/2020/02/kiesler10-Regulation-current.pdf).
Exercise 5, slide 30, explicitly identifies a pre-submission warning with an
opportunity to edit as a passable implementation. The preview implements this
mechanism; a reduction in offenses would need a user study to establish.
