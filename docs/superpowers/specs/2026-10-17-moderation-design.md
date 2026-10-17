# Assignment 2: moderation

User approved the moderation preview on 17 October 2026. Build this assignment
on `main` in `assignment-2`; keep Assignment 1 independent.

## Required rules

Use the supplied `/rules` template, checked against the live rules page, as the
specification. Tier 1 takes priority over Tier 2; either returns its exact removal
message and 5.0. Otherwise mask each whole Tier 3 word, remove each URL, add 2.0
per match, and add 0.5 when the original text has more than 15 letters and more
than 70% capitals. Content scores are not capped.

User risk is `(profile + 3 * average_posts + average_comments) * age_multiplier`,
capped at 5. Empty averages are zero. Multipliers are 1.5 before seven days, 1.2
before thirty days, and 1 otherwise. Do not divide the specified sum by five.
Retain original content for repeatable scoring; filter all public displays.

## Chosen feature and alternatives

Chapter 4, Design Claim 20: reminders at the point of a potentially norm-breaking
action can reduce offenses. The user chose an interactive preview over a static
reminder or a larger reporting system. The exercise slides specifically accept
a warning at submission with a chance to edit, and reject a front-page banner.

Every affected post, comment or signup introduction opens a private review page
before saving. Show the filtered preview, triggered rules, and an editable draft.
Allow rechecking and explicitly publishing the moderated result. Clean text
submits directly, with an optional Check before posting button. Re-score every
submission. Confirmation is tied to the reviewed text, content kind and target
post with a digest in Flask's signed session, so changed text needs another review.
Signup review preserves non-secret fields but requires the password again; never
include a password in hidden fields, the session or a preview. No JavaScript
is required. No database migrations or account sanctions are needed.

## Structure and verification

Implement the two required functions in app.py, with small helpers for matching,
rule feedback and confirmation. Reuse existing Bootstrap styling and one review
template. Enable HTML escaping for .j2 templates so previews and public text are
safe to render. Verify exact boundaries, repeated words, phrases, URL masking,
capitalization, weighted averages, account ages, public filtering, authentication,
changed-draft confirmation and no writes before approval. Use temporary databases
for tests and a separate seeded demo database. Preserve database.sqlite.

Provide a clear guide, a 400–500 word report draft answering the five questions,
and a two-minute recording script. The user must review personal reflections
and record/upload the video to Moodle.

## Sources

- Course assignment instructions, repository parent directory.
- `templates/rules.html.j2` and https://mini-social.szab.eu/rules
- Exercise/Social Computing Exercise 5 Moderation in MiniSocial.pptx, slides 28–31.
- Author's pre-copy-edited Chapter 4, Design Claim 20, p.21:
  https://kraut.hciresearch.info/wp-content/uploads/2020/02/kiesler10-Regulation-current.pdf

Reviewed for scope, consistency and missing decisions. No unresolved placeholders.
