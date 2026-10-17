# Assignment 3 implementation plan

1. Record the approved design and create assignment-3 from original main.
2. Implement recommendations in a small module using current reactions/follows;
   connect recommend() and return the chosen five newest first.
3. Add atomic introduction metadata and an optional public introduction hub;
   link it from signup, navigation and the feed.
4. Add a private server-rendered post/comment/reaction practice area with reset.
5. Verify ranking, cold start, strict filters, recommendation order, introductions,
   authentication, escaping, signup navigation and private practice isolation.
6. Seed an isolated demo, test desktop/mobile flows, write a 400–500 word report
   and a short recording script, make the demo recording, then commit/push.

Implementation uses existing Flask/SQLite/Jinja conventions and no new package.
The writing-plans skill referenced by brainstorming is not installed in this
workspace, so this plan records the implementation and verification sequence.

All steps completed. The 32 automated tests pass. Browser verification covers
practice, public introductions and welcoming replies, positive reactions,
follows, five-post selection and strict Following. The introduction hub was
also inspected at a 390-pixel mobile viewport. The annotated recording is
approximately 87 seconds long; report length is 458 words.
