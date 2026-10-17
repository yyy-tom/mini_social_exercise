"""Assignment 2 rule and publishing tests; never write the course database."""
import sqlite3
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import app as minisocial


class ContentModerationTests(unittest.TestCase):
    def test_clean_and_missing_text(self):
        for text in ('A friendly conversation.', '', None):
            with self.subTest(text=text):
                self.assertEqual(minisocial.moderate_content(text), (text or '', 0.0))

    def test_severe_removal_and_priority(self):
        for text in ('TIER1BADWORD!', 'tier2badword tier1badword tier3badword https://example.org'):
            with self.subTest(text=text):
                self.assertEqual(minisocial.moderate_content(text),
                                 ('[content removed due to severe violation]', 5.0))

    def test_spam_removal(self):
        self.assertEqual(minisocial.moderate_content('Try TIER2BADWORD now.'),
                         ('[content removed due to spam/scam policy]', 5.0))

    def test_mild_occurrences_case_and_length(self):
        text, score = minisocial.moderate_content('TIER3BADWORD, tier3badword.')
        self.assertEqual(text, '*' * len('tier3badword') + ', ' + '*' * len('tier3badword') + '.')
        self.assertEqual(score, 4.0)

    def test_whole_words_not_substrings(self):
        text = 'pretier1badword tier2badwords pretier3badword'
        self.assertEqual(minisocial.moderate_content(text), (text, 0.0))

    def test_whole_phrase_boundaries(self):
        with patch.object(minisocial, '_TIER2', minisocial._word_pattern(['claim a pretend prize'])):
            self.assertEqual(minisocial.moderate_content('Claim a pretend prize!')[1], 5.0)
            self.assertEqual(minisocial.moderate_content('Reclaim a pretend prize.')[1], 0.0)

    def test_literal_terms_are_escaped(self):
        pattern = minisocial._word_pattern(['fake+word'])
        self.assertIsNotNone(pattern.search('Fake+word!'))
        self.assertIsNone(pattern.search('fakeeeeeword'))

    def test_urls_masked_and_counted(self):
        self.assertEqual(minisocial.moderate_content('See https://example.org and WWW.example.net.'),
                         ('See [link removed] and [link removed].', 4.0))

    def test_url_parentheses(self):
        self.assertEqual(minisocial.moderate_content('See (https://example.org/a_(b)).'),
                         ('See ([link removed]).', 2.0))

    def test_each_violation_counts_without_content_cap(self):
        self.assertEqual(minisocial.moderate_content('tier3badword tier3badword https://example.org')[1], 6.0)

    def test_caps_length_threshold(self):
        self.assertEqual(minisocial.moderate_content('A' * 15)[1], 0.0)
        self.assertEqual(minisocial.moderate_content('A' * 16)[1], 0.5)

    def test_caps_percentage_threshold(self):
        self.assertEqual(minisocial.moderate_content('A' * 14 + 'a' * 6)[1], 0.0)
        self.assertEqual(minisocial.moderate_content('A' * 15 + 'a' * 5)[1], 0.5)

    def test_caps_use_original_letters(self):
        original = 'A' * 16 + ' https://example.org/alonglowercasepath'
        self.assertEqual(minisocial.moderate_content(original)[1], 2.0)

    def test_caps_ignore_punctuation_and_digits(self):
        self.assertEqual(minisocial.moderate_content('A' * 16 + ' 1234!?')[1], 0.5)


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = str(Path(self.temp.name) / 'test.sqlite')
        self.database_patch = patch.object(minisocial, 'DATABASE', self.path)
        self.database_patch.start()
        self.addCleanup(self.database_patch.stop)
        self.context = minisocial.app.app_context()
        self.context.push()
        self.addCleanup(self.context.pop)
        minisocial.app.config['TESTING'] = True
        db = minisocial.get_db()
        # Use the course schema verbatim, opening the supplied file read-only.
        uri = (Path(__file__).resolve().parents[1] / 'database.sqlite').as_uri() + '?mode=ro'
        with sqlite3.connect(uri, uri=True) as source:
            for (schema,) in source.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence'"):
                db.execute(schema)
        old = (datetime.now(timezone.utc) - timedelta(days=40)).strftime('%Y-%m-%d %H:%M:%S')
        db.executemany('INSERT INTO users (id,username,profile,created_at,password) VALUES (?,?,?,?,?)',
                       [(1, 'alice', '', old, ''), (2, 'admin', '', old, '')])
        db.executemany('INSERT INTO posts (id,user_id,content) VALUES (?,?,?)',
                       [(1, 2, 'Welcome to our study group.'), (2, 2, 'Another friendly discussion.')])
        db.commit()
        self.client = minisocial.app.test_client()

    def login_as(self, user_id=1, username='alice'):
        with self.client.session_transaction() as session:
            session['user_id'] = user_id
            session['username'] = username

    def scalar(self, query, params=()):
        return minisocial.get_db().execute(query, params).fetchone()[0]

    def add_post(self, text):
        db = minisocial.get_db()
        db.execute('INSERT INTO posts(user_id,content) VALUES (1,?)', (text,))
        db.commit()


class UserRiskTests(DatabaseTests):
    def test_missing_user_or_empty_history(self):
        self.assertEqual(minisocial.user_risk_analysis(999), 0.0)
        self.assertEqual(minisocial.user_risk_analysis(1), 0.0)

    def test_averages_and_weights_not_divided_by_five(self):
        self.add_post('tier3badword')
        self.add_post('A friendly conversation.')
        db = minisocial.get_db()
        db.execute('UPDATE users SET profile=? WHERE id=1', ('A' * 16,))
        db.execute('INSERT INTO comments(post_id,user_id,content) VALUES (1,1,?)', ('tier3badword',))
        db.execute('INSERT INTO comments(post_id,user_id,content) VALUES (1,1,?)', ('A friendly reply.',))
        db.commit()
        self.assertEqual(minisocial.user_risk_analysis(1), 4.5)  # .5 + 3*(2/2) + 2/2

    def test_age_multipliers_and_boundaries(self):
        self.add_post('A' * 16)  # .5 * 3 = 1.5 before age multiplier
        for age, expected in [(0, 2.25), (6, 2.25), (7, 1.8), (29, 1.8), (30, 1.5)]:
            with self.subTest(age=age), patch.object(minisocial, 'account_age_days', return_value=age):
                self.assertAlmostEqual(minisocial.user_risk_analysis(1), expected)

    def test_user_score_is_capped(self):
        self.add_post('tier1badword')
        self.assertEqual(minisocial.user_risk_analysis(1), 5.0)

    def test_other_users_do_not_affect_score(self):
        self.add_post('A friendly conversation.')
        self.assertEqual(minisocial.user_risk_analysis(2), 0.0)

    def test_utc_age_boundaries(self):
        fixed = datetime(2026, 10, 17, 12, tzinfo=timezone.utc)
        class FixedDateTime(datetime):
            @classmethod
            def now(cls, tz=None):
                return fixed
        with patch.object(minisocial, 'datetime', FixedDateTime):
            for age in (6, 7, 29, 30):
                created = fixed - timedelta(days=age)
                self.assertEqual(minisocial.account_age_days(created.replace(tzinfo=None)), age)
                self.assertEqual(minisocial.account_age_days(created.isoformat()), age)
            self.assertEqual(minisocial.account_age_days(None), 0)


class PublishingTests(DatabaseTests):
    def test_login_required(self):
        for path in ('/posts/new', '/posts/1/comment'):
            response = self.client.post(path, data={'content': 'tier1badword'})
            self.assertEqual(response.status_code, 302)
            self.assertIn('/login', response.location)
        self.assertEqual(self.scalar('SELECT COUNT(*) FROM posts'), 2)

    def test_clean_post_saves_directly(self):
        self.login_as()
        self.assertEqual(self.client.post('/posts/new', data={'content': 'A friendly conversation.'}).status_code, 302)
        self.assertEqual(self.scalar('SELECT COUNT(*) FROM posts'), 3)

    def test_affected_post_is_not_saved_until_confirmed(self):
        self.login_as()
        data = {'content': 'tier3badword https://example.org'}
        review = self.client.post('/posts/new', data=data)
        self.assertIn(b'Check before publishing', review.data)
        self.assertIn(b'Content score: <strong>4.0</strong>', review.data)
        self.assertEqual(self.scalar('SELECT COUNT(*) FROM posts'), 2)
        response = self.client.post('/posts/new', data={**data, 'moderation_action': 'publish'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.scalar('SELECT content FROM posts WHERE id=3'), data['content'])
        self.assertNotIn(b'https://example.org', self.client.get('/posts/3').data)
        self.assertIn(b'[link removed]', self.client.get('/posts/3').data)

    def test_publish_without_review_is_blocked(self):
        self.login_as()
        response = self.client.post('/posts/new', data={'content': 'tier1badword', 'moderation_action': 'publish'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.scalar('SELECT COUNT(*) FROM posts'), 2)

    def test_changing_flagged_draft_needs_review(self):
        self.login_as()
        self.client.post('/posts/new', data={'content': 'tier3badword'})
        response = self.client.post('/posts/new', data={'content': 'tier1badword', 'moderation_action': 'publish'})
        self.assertIn(b'severe violation', response.data)
        self.assertEqual(self.scalar('SELECT COUNT(*) FROM posts'), 2)

    def test_comment_review_is_bound_to_target_post(self):
        self.login_as()
        data = {'content': 'tier3badword'}
        self.client.post('/posts/1/comment', data=data)
        self.assertEqual(self.scalar('SELECT COUNT(*) FROM comments'), 0)
        self.assertEqual(self.client.post('/posts/2/comment', data={**data, 'moderation_action': 'publish'}).status_code, 200)
        self.assertEqual(self.scalar('SELECT COUNT(*) FROM comments'), 0)
        self.assertEqual(self.client.post('/posts/2/comment', data={**data, 'moderation_action': 'publish'}).status_code, 302)
        self.assertEqual(self.scalar('SELECT COUNT(*) FROM comments'), 1)

    def test_revising_to_clean_text_avoids_the_violation(self):
        self.login_as()
        self.client.post('/posts/new', data={'content': 'tier3badword'})
        self.client.post('/posts/new', data={'content': 'Thanks for sharing your idea.'})
        self.assertEqual(minisocial.user_risk_analysis(1), 0.0)

    def test_optional_clean_preview_does_not_write(self):
        self.login_as()
        response = self.client.post('/posts/new', data={'content': 'A friendly conversation.', 'moderation_action': 'preview'})
        self.assertIn(b'No moderation rules were triggered', response.data)
        self.assertEqual(self.scalar('SELECT COUNT(*) FROM posts'), 2)

    def test_empty_post_and_nonexistent_target_do_not_write(self):
        self.login_as()
        self.client.post('/posts/new', data={'content': '   '})
        self.assertEqual(self.client.post('/posts/999/comment', data={'content': 'A friendly reply.'}).status_code, 404)
        self.assertEqual(self.scalar('SELECT COUNT(*) FROM posts'), 2)
        self.assertEqual(self.scalar('SELECT COUNT(*) FROM comments'), 0)

    def test_signup_review_does_not_keep_password(self):
        data = {'username': 'carol', 'password': 'do-not-echo-me', 'profile': 'tier3badword',
                'location': 'Oulu', 'birthdate': '2000-01-01'}
        response = self.client.post('/signup', data=data)
        self.assertIn(b'Re-enter your password', response.data)
        self.assertNotIn(b'do-not-echo-me', response.data)
        with self.client.session_transaction() as session:
            self.assertNotIn('do-not-echo-me', str(dict(session)))
        self.assertEqual(self.scalar('SELECT COUNT(*) FROM users'), 2)
        response = self.client.post('/signup', data={**data, 'moderation_action': 'publish'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.scalar("SELECT profile FROM users WHERE username='carol'"), 'tier3badword')
        self.assertNotIn(b'tier3badword', self.client.get('/u/carol').data)

    def test_preview_and_public_views_escape_html(self):
        self.login_as()
        draft = '<script>alert(1)</script> tier3badword'
        response = self.client.post('/posts/new', data={'content': draft})
        self.assertNotIn(b'<script>alert(1)</script>', response.data)
        self.assertIn(b'&lt;script&gt;', response.data)
        self.client.post('/posts/new', data={'content': draft, 'moderation_action': 'publish'})
        for path in ('/', '/posts/3', '/u/alice'):
            response = self.client.get(path)
            self.assertNotIn(b'<script>alert(1)</script>', response.data)
            self.assertIn(b'&lt;script&gt;', response.data)
            self.assertNotIn(b'tier3badword', response.data)

    def test_public_comments_filtered_in_all_views(self):
        db = minisocial.get_db()
        db.execute('INSERT INTO comments(post_id,user_id,content) VALUES(1,1,?)', ('tier1badword',))
        db.commit()
        for path in ('/', '/posts/1', '/u/alice'):
            self.assertNotIn(b'tier1badword', self.client.get(path).data)
            self.assertIn(b'[content removed due to severe violation]', self.client.get(path).data)

    def test_admin_access_and_age_adjusted_scores(self):
        self.assertEqual(self.client.get('/admin').status_code, 302)
        self.login_as(2, 'admin')
        self.add_post('tier3badword')
        with patch.object(minisocial, 'account_age_days', return_value=0):
            response = self.client.get('/admin')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'3.0', response.data)  # content 2 * new-account 1.5
        self.assertIn(b'5.0', response.data)  # user score is capped


if __name__ == '__main__':
    unittest.main()
