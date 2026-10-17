# Assignment 2 implementation plan

1. Branch from original main; record the approved preview design. Done.
2. Implement tier precedence, literal whole-word/phrase matching, masking, URL
   removal, original-text capitalization and exact scores. Done.
3. Implement weighted user scoring with UTC account-age boundaries and capping.
   Reuse the age helper for admin post/comment scores. Done.
4. Intercept affected post/comment/signup submissions with a server-rendered
   preview. Require the reviewed draft before confirmation. Keep passwords out
   of previews and enable .j2 HTML escaping. Done.
5. Verify rules and publishing through isolated SQLite and Flask tests. Done.
6. Create a separate demo dataset, check browser flows, write report and video
   script and annotated video, and push assignment-2 for review. Done.
   See the accompanying guide.
