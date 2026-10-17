# Coding Assignment 3: Dealing with newcomers

**Draft for review:** Adjust the learning and difficulty paragraphs to match your
own experience, and review the AI-generated code and demo before submitting.
Copy the text below into Moodle, including the questions and repository link.

---

**What features did you implement, and how does each implemented feature function?**

For Assignment 3, I added personalised post recommendations, an introduction hub and a private practice area to MiniSocial.

The Recommended tab selects up to five posts using the member's positive reactions and the people they follow. It compares words in posts using TF-IDF, which gives more weight to distinctive terms, and adds a bonus for followed authors. It leaves out the member's own posts and posts they have already reacted to. After selecting the five strongest matches, it displays them newest first. Members without any activity see recent posts, while the Following filter only shows posts from followed accounts.

The introduction hub lets members write an optional public introduction. Each introduction becomes a normal post that others can reply to, and the hub makes these conversations easy to find. Members can also practise posting, replying and reacting in a separate area. Practice actions never enter the public database.

**How does the feature fulfil the Design Claim (see course book) it aims to implement?**

The introduction hub follows Chapter 5, Design Claim 19. Public introductions give existing members something to talk about with newcomers. For example, someone who mentions an interest in woodworking gives another member a reason to ask about their projects. The “Say hello” link opens that introduction's comments, so the feature supports an actual conversation.

The practice area follows Design Claim 24, which proposes sandboxes as a way to help newcomers learn while reducing possible harm to the community. Members can try the same kinds of actions they will use publicly, see the results and reset their practice. They can make mistakes without filling the real feed with test posts. These features implement the claims' mechanisms; their effects on learning and interaction would need a user study.

**What did you learn during the coding assignment?**

The recommendation feature helped me understand how a system can work with limited information about a member. A new account has no reaction history, so it needs a sensible starting point. The newcomer features also show why learning how to participate and feeling comfortable enough to participate are separate problems.

**What was difficult, if anything?**

The main challenges were separating recommendation ranking from display order and keeping practice completely separate from public activity. Introduction submissions also needed protection against duplicate clicks. Tests check these details, including simultaneous submissions, filtering and practice isolation.

**How was AI used in your assignment?**

I used AI extensively to interpret the requirements, suggest the features and generate the code and tests. It also checked the browser flows and helped prepare this report and the demo materials. I need to review the result so I can explain the implementation and its limitations myself.

Repository: https://github.com/yyy-tom/mini_social_exercise/tree/assignment-3
