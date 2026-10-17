# Coding Assignment 2: Moderation

**Draft for review:** Read the report and adjust the learning and difficulty
paragraphs to match your own experience before submitting. Copy the text below
into Moodle, keeping the five questions. Review the supplied annotated video too.

---

**What features did you implement, and how does each implemented feature function?**

For Assignment 2, I added a content filter and user risk scores to MiniSocial. I also added a preview so members can see what will happen to their message before sharing it.

The filter follows the supplied rules. A Tier 1 word or Tier 2 spam phrase replaces the whole text with a removal message and gives it a score of 5. Milder Tier 3 words are covered with asterisks, and external links are removed. Each match adds 2 points. Text with more than 15 letters gets another 0.5 points if over 70% are capitals. The filter ignores case and checks whole words to avoid catching harmless words that contain a listed term.

User risk combines the profile score, three times the average post score and the average comment score. Newer accounts receive the required multiplier, and the final score is capped at 5. The admin dashboard displays these scores for review.

**How does the feature fulfil the Design Claim (see course book) it aims to implement?**

I chose Chapter 4, Design Claim 20, which suggests that reminders at the moment someone might break a rule can reduce offenses.

When a post, comment or profile introduction triggers a rule, MiniSocial opens a private review before saving anything. It shows the filtered text and explains what caused the warning. Members can edit their draft, check it again or publish the filtered version.

For example, someone who writes an angry reply can replace it with a calmer response before others see it. The reminder comes while they can still change their mind. Whether this actually reduces offenses would need testing with real users.

**What did you learn during the coding assignment?**

The assignment helped me understand why message scores and user scores need different calculations. One message can score above 5, but the account score has a limit. Another detail was keeping the original text for risk analysis. If the system only kept the censored version, later checks would lose the evidence of what triggered the filter.

**What was difficult, if anything?**

The tricky parts were the small details: counting repeated words correctly and applying the age multiplier at exactly seven and thirty days. The preview also had to check edited drafts again, so someone could not review one message and then publish a different flagged message without another check. Automated tests cover these cases.

**How was AI used in your assignment?**

I used AI extensively to interpret the instructions, suggest the preview and generate the code and tests. It also checked the app in the browser, created the annotated demo video and helped write this report. I still need to review the work and make sure I can explain how it behaves.

Repository: https://github.com/yyy-tom/mini_social_exercise/tree/assignment-2
