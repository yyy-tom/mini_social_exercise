# Assignment 3 two-minute demo

Use the separate Assignment 3 database. All demo accounts use `demo-password`.
Start as `demo_alice`, who has no introduction, follows or reactions. Prepare
another session as `demo_bob`, or switch accounts while recording. An annotated
recording is supplied separately; this script also supports a personal recording.

| Time | Show | Explain |
|---|---|---|
| 0:00–0:08 | Alice's home page and the newcomer links. | “Assignment 3 adds personalised recommendations and two features to help newcomers participate.” |
| 0:08–0:32 | Open Private practice. Post a short question, click Like privately, add a friendly reply. Show 3/3 complete. | “Chapter 5 Claim 24 proposes sandboxes for learning with less harm. I can try posting, replying and reacting here. These actions do not create public posts, comments or reactions.” |
| 0:32–0:49 | Open Introductions. Publish `Hi everyone! I enjoy DIY woodworking and would love to learn about simple workshop projects.` | “The optional introduction hub follows Claim 19. It gives established members something to start a conversation about.” |
| 0:49–1:06 | Log in as Bob, open Introductions, choose Say hello for Alice and add `Welcome, Alice! What would you like to build first?` | “Introductions become real posts. Existing members can reply through the normal comment flow, so this creates a conversation rather than just a profile label.” |
| 1:06–1:23 | Switch back to Alice. Open post 1 and give it a Like. Open Bob's profile and Follow. | “The recommendation algorithm learns from positive reactions and followed authors. Alice has now shown an interest in DIY woodworking.” |
| 1:23–1:43 | Open Recommended; show the five selected DIY posts and their explanations. | “It compares distinctive words using TF-IDF and cosine similarity, then adds a bonus for followed authors. It selects five relevant posts and displays them newest first. Own and already-reacted posts are excluded.” |
| 1:43–1:54 | Click Following; show that only Bob's eligible posts remain. | “Following is a strict filter. Without any history, the All view starts with recent posts. It can show fewer than five when fewer eligible posts exist.” |
| 1:54–1:59 | End on the recommendations. | “The recommender helps members find conversations, while introductions and practice give them ways to join in.” |

Private practice is separate from Assignment 2's moderation preview. No practice
button can publish its text into the real feed. The chapter claims motivate the
features; a user study would be needed to measure their actual effects.
