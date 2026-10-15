"""Behavior checks against isolated SQLite data; never edit the course database."""

from datetime import datetime, timedelta, timezone
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

import app as mini_social
from contribution import community_week, contribution_dashboard


NOW = datetime(2026, 10, 15, 12, tzinfo=timezone.utc)
SCHEMA = """
CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT);
CREATE TABLE posts (
    id INTEGER PRIMARY KEY, user_id INTEGER, content TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE comments (
    id INTEGER PRIMARY KEY, post_id INTEGER, user_id INTEGER, content TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE follows (follower_id INTEGER, followed_id INTEGER);
CREATE TABLE reactions (id INTEGER PRIMARY KEY, post_id INTEGER, user_id INTEGER, reaction_type TEXT);
"""


def seed_database(db):
    db.executescript(SCHEMA)
    db.executemany(
        'INSERT INTO users (id, username) VALUES (?, ?)',
        [(1, 'alice'), (2, 'bob'), (3, 'carol')],
    )
    db.executemany(
        'INSERT INTO posts (id, user_id, content, created_at) VALUES (?, ?, ?, ?)',
        [(1, 1, 'Alice asks a question', '2026-10-01 12:00:00')]
        + [(i, 2 if i % 2 == 0 else 3, f'Question {i}', '2026-10-15 09:00:00') for i in range(2, 9)],
    )
    db.commit()


class ContributionTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(':memory:', detect_types=sqlite3.PARSE_DECLTYPES)
        self.db.row_factory = sqlite3.Row
        seed_database(self.db)
        self.addCleanup(self.db.close)

    def comment(self, post=2, author=1, timestamp='2026-10-15 10:00:00', content='A reply'):
        cur = self.db.execute(
            'INSERT INTO comments (post_id, user_id, content, created_at) VALUES (?, ?, ?, ?)',
            (post, author, content, timestamp),
        )
        self.db.commit()
        return cur.lastrowid

    def dashboard(self, user=1):
        return contribution_dashboard(self.db, user, NOW)

    def test_week_is_monday_to_monday_in_helsinki(self):
        week = community_week(NOW)
        self.assertEqual(week['start_utc'], '2026-10-11 21:00:00')
        self.assertEqual(week['end_utc'], '2026-10-18 21:00:00')
        self.assertEqual(str(week['last_day']), '2026-10-18')

    def test_local_monday_can_still_be_sunday_in_utc(self):
        week = community_week(datetime(2026, 10, 11, 22, tzinfo=timezone.utc))
        self.assertEqual(week['start'].weekday(), 0)
        self.assertEqual(week['start_utc'], '2026-10-11 21:00:00')

    def test_dst_week_has_correct_utc_boundaries(self):
        week = community_week(datetime(2026, 10, 25, 12, tzinfo=timezone.utc))
        self.assertEqual(week['start_utc'], '2026-10-18 21:00:00')
        self.assertEqual(week['end_utc'], '2026-10-25 22:00:00')

    def test_naive_clock_is_rejected(self):
        with self.assertRaises(ValueError):
            community_week(datetime(2026, 10, 15))

    def test_needs_reply_excludes_self_and_has_five_newest(self):
        self.assertEqual([p['id'] for p in self.dashboard()['needs_reply']], [8, 7, 6, 5, 4])

    def test_any_comment_removes_opportunity_even_post_authors_reply(self):
        self.comment(post=8, author=2)
        self.assertNotIn(8, [p['id'] for p in self.dashboard()['needs_reply']])

    def test_needs_reply_empty_state_data(self):
        for post in range(2, 9):
            self.comment(post=post)
        self.assertEqual(self.dashboard()['needs_reply'], [])

    def test_duplicate_comments_self_replies_and_other_members_do_not_inflate_goal(self):
        self.comment(post=2)
        self.comment(post=2)
        self.comment(post=1)
        self.comment(post=3, author=2)
        self.assertEqual(self.dashboard()['goal']['completed'], 1)

    def test_goal_uses_comment_time_and_half_open_week_bounds(self):
        week = community_week(NOW)
        self.comment(post=2, timestamp=week['start_utc'])
        self.comment(post=3, timestamp=week['end_utc'])
        before_start = week['start'].astimezone(timezone.utc) - timedelta(seconds=1)
        self.comment(post=4, timestamp=before_start.strftime('%Y-%m-%d %H:%M:%S'))
        self.assertEqual(self.dashboard()['goal']['completed'], 1)

    def test_goal_completion_caps_display_and_bar_but_keeps_total(self):
        for post in range(2, 6):
            self.comment(post=post)
        goal = self.dashboard()['goal']
        self.assertEqual(goal['completed'], 4)
        self.assertEqual(goal['display_completed'], 3)
        self.assertEqual(goal['percent'], 100)
        self.assertTrue(goal['achieved'])

    def test_removed_comments_and_orphaned_comments_do_not_count(self):
        comment_id = self.comment(post=2)
        self.comment(post=999)
        self.db.execute('DELETE FROM comments WHERE id = ?', (comment_id,))
        self.assertEqual(self.dashboard()['goal']['completed'], 0)

    def test_support_counts_comments_and_distinct_other_members_on_old_posts(self):
        self.comment(post=1, author=2)
        self.comment(post=1, author=2)
        self.comment(post=1, author=3)
        self.comment(post=1, author=1)
        self.comment(post=1, author=2, timestamp='2026-10-01 12:00:00')
        self.comment(post=1, author=3, timestamp=community_week(NOW)['end_utc'])
        self.comment(post=2, author=3)
        self.assertEqual(self.dashboard()['support'], {'comments': 3, 'members': 2})

    def test_recent_support_links_are_limited_sorted_and_belong_to_recipient(self):
        ids = [self.comment(post=1, author=2, content=f'Reply {i}') for i in range(5)]
        self.comment(post=2, author=3)
        comments = self.dashboard()['recent_support']
        self.assertEqual([c['id'] for c in comments], list(reversed(ids[-3:])))
        self.assertTrue(all(c['post_id'] == 1 for c in comments))

    def test_new_member_has_honest_zero_counts(self):
        data = self.dashboard()
        self.assertEqual(data['goal']['percent'], 0)
        self.assertFalse(data['goal']['achieved'])
        self.assertEqual(data['support'], {'comments': 0, 'members': 0})
        self.assertEqual(data['recent_support'], [])


class FeedIntegrationTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = str(Path(directory.name) / 'test.sqlite')
        with sqlite3.connect(path) as db:
            seed_database(db)
        database_patch = patch.object(mini_social, 'DATABASE', path)
        database_patch.start()
        self.addCleanup(database_patch.stop)
        testing_patch = patch.dict(mini_social.app.config, TESTING=True)
        testing_patch.start()
        self.addCleanup(testing_patch.stop)
        self.client = mini_social.app.test_client()

    def sign_in(self, user=1, username='alice'):
        with self.client.session_transaction() as session:
            session.clear()
            session['user_id'] = user
            session['username'] = username

    def test_anonymous_feed_has_no_personal_dashboard(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b'Your community corner', response.data)

    def test_signed_in_feed_has_three_features_and_accessible_progress(self):
        self.sign_in()
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        for text in (b'Needs a reply', b'Your weekly goal', b'Support you received',
                     b'role="progressbar"', b'aria-valuenow="0"', b'No replies to your posts'):
            self.assertIn(text, response.data)

    def test_following_filter_does_not_hide_community_opportunities(self):
        self.sign_in()
        response = self.client.get('/?show=following&sort=popular&page=2')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'No posts to display.', response.data)
        self.assertIn(b'data-post-id="8"', response.data)
        self.assertIn(b'Your weekly goal', response.data)

    def test_removed_post_detail_returns_not_found(self):
        self.assertEqual(self.client.get('/posts/999').status_code, 404)

    def test_reply_updates_both_accounts_and_removes_opportunity(self):
        self.sign_in()
        response = self.client.post('/posts/8/comment', data={'content': 'Here is an idea'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Weekly goal: 1/3 posts.', response.data)
        response = self.client.get('/')
        self.assertIn(b'1 / 3 posts', response.data)
        self.assertNotIn(b'data-post-id="8"', response.data)
        self.sign_in(2, 'bob')
        response = self.client.get('/?user_id=1')
        self.assertIn(b'1 member has', response.data)
        self.assertIn(b'alice replied: Here is an idea', response.data)
        self.assertIn(b'/posts/8#comment-1', response.data)
        self.assertIn(b'0 / 3 posts', response.data)
        self.assertIn(b'id="comment-1"', self.client.get('/posts/8').data)

    def test_repeated_replies_do_not_advance_goal_and_completion_is_visible(self):
        self.sign_in()
        for post in (2, 2, 3):
            self.client.post(f'/posts/{post}/comment', data={'content': 'A reply'})
        self.assertIn(b'2 / 3 posts', self.client.get('/').data)
        response = self.client.post('/posts/4/comment', data={'content': 'Another reply'}, follow_redirects=True)
        self.assertIn(b'Weekly goal complete', response.data)
        self.assertIn(b'Goal complete!', self.client.get('/').data)

    def test_self_and_empty_comments_do_not_advance_goal(self):
        self.sign_in()
        self.client.post('/posts/1/comment', data={'content': 'My own reply'})
        self.client.post('/posts/8/comment', data={'content': '  '})
        response = self.client.get('/')
        self.assertIn(b'0 / 3 posts', response.data)
        self.assertIn(b'data-post-id="8"', response.data)

    def test_missing_post_does_not_create_orphaned_reply(self):
        self.sign_in()
        response = self.client.post('/posts/999/comment', data={'content': 'A reply'}, follow_redirects=True)
        self.assertIn(b'This post is no longer available.', response.data)
        with mini_social.app.app_context():
            self.assertEqual(mini_social.get_db().execute('SELECT COUNT(*) FROM comments').fetchone()[0], 0)

    def test_anonymous_comment_redirects_to_login(self):
        response = self.client.post('/posts/8/comment', data={'content': 'A reply'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith('/login'))

    def test_preview_content_is_escaped(self):
        self.sign_in()
        with mini_social.app.app_context():
            mini_social.get_db().execute("UPDATE posts SET content = ? WHERE id = 8", ('<script>alert(1)</script>',))
            mini_social.get_db().commit()
        response = self.client.get('/')
        self.assertNotIn(b'<script>alert(1)</script>', response.data)
        self.assertIn(b'&lt;script&gt;alert(1)&lt;/script&gt;', response.data)


if __name__ == '__main__':
    unittest.main()
