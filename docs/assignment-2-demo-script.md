# Assignment 2: two-minute demo

Use the separate Assignment 2 database. Prepare two browser sessions: demo_alice
with demo-password and admin with admin. If using one window, log out and back in.
Keep the recording below two minutes; aim for 1:50. This file is a script, not a
recording. Do not use the production/course dataset for recording experiments.

| Time | Show | Say |
|---|---|---|
| 0:00–0:12 | Log in as demo_alice. | “This is my Assignment 2 version of MiniSocial. I added content moderation, user risk analysis and a chance to revise a message before publishing.” |
| 0:12–0:35 | Enter `I disagree. tier3badword https://example.org` in the new-post box. Click Post. | “This submission opens a private review before anything is saved. The mild test word is masked, the link is removed, and each adds two points. I can see the result other members would see.” |
| 0:35–0:55 | Replace the draft with `I see it differently. Could you explain your reasoning?` Click Check revision, then Publish moderated post. | “I can rewrite my message and check it again. This clean version scores zero. This implements Chapter 4 Design Claim 20: a reminder at the point of action gives people a chance to avoid breaking a rule.” |
| 0:55–1:12 | Enter `tier1badword` in a new post and click Post. Show severe-removal preview, then Cancel. | “Severe language removes the whole text and scores five. Spam phrases receive a different removal message. A warning alone does not publish anything.” |
| 1:12–1:30 | Open Bob’s post, add `tier3badword` as a comment. Show preview, then Cancel. | “The same check applies to comments and signup introductions. I can revise, cancel or choose to publish the filtered result.” |
| 1:30–1:52 | Switch to admin at /admin. Show Users, then Comments. | “The admin dashboard combines profile risk, three times average post risk and average comment risk. It applies the required age multiplier and caps user risk at five. Bob’s mild comment scores three because his account is under seven days old.” |
| 1:52–1:58 | End on dashboard. | “The automated filter limits harmful content, while the preview helps members correct their own messages.” |

Safe course test tokens: tier1badword, tier2badword, tier3badword. These are
intentional placeholders in the supplied word lists; no real abusive examples
are needed. Alice's account score remains 2.0 after the clean post above. Bob is
initially 3.0 and Carol 5.0. Bob's new-account multiplier changes after seven days;
create a fresh demo under a new output filename if recording later.
