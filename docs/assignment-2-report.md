# Coding Assignment 2: Moderation

**Draft for review:** Read the report and adjust the learning and difficulty
paragraphs to match your own experience before submitting. Copy the text below
into Moodle, keeping the five questions. Review the supplied annotated video too.

---

**What features did you implement, and how does each implemented feature function?**

For this assignment, I added automatic moderation, user risk analysis and a preview that lets members check their text before publishing it.

The moderation function follows MiniSocial’s rules. A Tier 1 word removes the entire text with a severe-violation message and a score of 5. A Tier 2 spam or scam phrase also removes the text with its own message and the same score. Otherwise, each Tier 3 word is replaced with asterisks and adds 2 points. Each external link is removed and adds another 2 points. Text with more than 15 letters receives an extra 0.5 points when over 70% of those letters are uppercase. Matching ignores case and avoids censoring words simply because they contain a listed word.

The user risk function combines the profile score, three times the average post score and the average comment score. It applies the required account-age multiplier and caps the result at 5. Missing posts or comments contribute zero. Administrators can inspect these scores in the existing dashboard.

**How does the feature fulfil the Design Claim it aims to implement?**

The preview follows Chapter 4, Design Claim 20: reminders at the point of a potentially rule-breaking action can reduce offenses. When a post, comment or introduction triggers moderation, MiniSocial pauses before saving it. The member sees the filtered result, an explanation of the triggered rules and a link to the rules page.

They can rewrite the draft, check it again or explicitly publish the moderated version. A changed draft is checked again before any affected text is published. This gives someone a practical chance to fix a message while they are still deciding what to share. The feature implements the claim’s proposed mechanism; it does not prove that offenses decrease without a user study.

**What did you learn during the coding assignment?**

This implementation helped me understand the difference between filtering one message and estimating risk across an account’s history. A single content score can exceed 5, while the final user score is capped. Keeping the original text also matters: calculating risk from already censored text would hide the violations from later analysis.

**What was difficult, if anything?**

The main implementation challenges were matching whole words, handling the exact age boundaries and keeping the preview consistent with publication. Tests cover those cases, including repeated violations and drafts changed after review. The signup preview also requires the password again so it is never carried through the preview page.

**How was AI used in your assignment?**

I used AI extensively to interpret the requirements, propose the preview, generate the implementation and tests, and draft this report and the demo script. AI also ran automated checks and browser verification, and produced an annotated demo recording. The code and report need my review so I can explain their behaviour accurately.

Repository: https://github.com/yyy-tom/mini_social_exercise/tree/assignment-2
