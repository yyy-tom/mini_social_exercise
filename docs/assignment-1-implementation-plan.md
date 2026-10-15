# Assignment 1 implementation plan

Design approved by the user: `superpowers/specs/2026-10-15-contribution-and-commitment-design.md`.

1. Implement read-only dashboard queries and Helsinki week boundaries in a small
   module. Use the existing request database connection and no stored counters.
2. Add the authenticated feed partial, progress feedback, unanswered-post links,
   received-support links, and comment anchors. Follow the existing page style.
3. Add isolated standard-library tests of the behavioral rules and the real Flask
   comment submission flow. Verify that the supplied database is unchanged.
4. Install the existing dependencies in a local virtual environment, run tests,
   and check desktop/mobile layout and the reply journey in a browser.
5. Document launch commands and a two-account demonstration; commit and push the
   finished code to the user's GitHub fork.
