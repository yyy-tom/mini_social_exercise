"""Assignment 3 integration tests on disposable SQLite databases only."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

import app as minisocial
from newcomers import own_introduction, publish_introduction
from recommendations import recommended_posts


class DatabaseCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = str(Path(self.temp.name) / 'test.sqlite')
        change_db = patch.object(minisocial, 'DATABASE', self.path)
        change_db.start()
        self.addCleanup(change_db.stop)
        self.context = minisocial.app.app_context()
        self.context.push()
        self.addCleanup(self.context.pop)
        minisocial.app.config['TESTING'] = True
        self.db = minisocial.get_db()
        uri = (Path(__file__).resolve().parents[1] / 'database.sqlite').as_uri() + '?mode=ro'
        with sqlite3.connect(uri, uri=True) as source:
            for (schema,) in source.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name!='sqlite_sequence'"):
                self.db.execute(schema)
        self.db.executemany('INSERT INTO users(id,username,password,profile) VALUES(?,?,?,?)',
                            [(1,'alice','',''),(2,'bob','',''),(3,'carol','',''),(4,'dave','','')])
        self.db.commit()
        self.client = minisocial.app.test_client()

    def login(self, user_id=1, username='alice'):
        with self.client.session_transaction() as session:
            session['user_id'], session['username'] = user_id, username

    def post(self, post_id, content, user_id=2, day=None):
        day = day or post_id
        self.db.execute('INSERT INTO posts(id,user_id,content,created_at) VALUES(?,?,?,?)',
                        (post_id,user_id,content,f'2026-10-{day:02d} 12:00:00'))
        self.db.commit()

    def react(self, post_id, reaction='like'):
        self.db.execute('INSERT INTO reactions(post_id,user_id,reaction_type) VALUES(?,1,?)', (post_id,reaction))
        self.db.commit()

    def follow(self, user_id=2):
        self.db.execute('INSERT INTO follows(follower_id,followed_id) VALUES(1,?)', (user_id,))
        self.db.commit()

    def ids(self, user_id=1, following=False):
        return [post['id'] for post in recommended_posts(self.db,user_id,following)]

    def counts(self):
        return {table:self.db.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]
                for table in ('users','posts','comments','reactions','follows','introductions')}


class RecommendationTests(DatabaseCase):
    def test_empty_database_returns_list(self):
        self.assertEqual(self.ids(), [])
        self.assertEqual(self.ids(None), [])

    def test_cold_start_five_latest_with_tie_break(self):
        for i in range(1,8): self.post(i,'A new discussion.',day=1)
        self.assertEqual(self.ids(), [7,6,5,4,3])
        self.assertEqual(self.ids(None), [7,6,5,4,3])

    def test_positive_history_selects_older_relevant_posts_then_displays_newest_first(self):
        self.post(1,'woodworking timber workshop')
        self.react(1)
        for i in range(2,7): self.post(i,'woodworking timber workshop project')
        for i in range(7,12): self.post(i,'violin orchestra concert music',user_id=3)
        self.assertEqual(self.ids(), [6,5,4,3,2])

    def test_all_positive_types_including_legacy_haha(self):
        self.post(1,'woodworking timber workshop')
        for i in range(2,7): self.post(i,'woodworking timber workshop project')
        for i in range(7,12): self.post(i,'violin orchestra concert music',user_id=3)
        for reaction in ('like','love','laugh','haha','wow'):
            self.db.execute('DELETE FROM reactions')
            self.db.commit()
            self.react(1,reaction)
            with self.subTest(reaction=reaction): self.assertEqual(self.ids(),[6,5,4,3,2])

    def test_negative_reactions_do_not_build_interests(self):
        self.post(1,'woodworking timber workshop')
        for i in range(2,7): self.post(i,'woodworking timber workshop')
        for i in range(7,12): self.post(i,'violin orchestra concert',user_id=3)
        for reaction in ('sad','angry'):
            self.db.execute('DELETE FROM reactions'); self.db.commit(); self.react(1,reaction)
            with self.subTest(reaction=reaction): self.assertEqual(self.ids(),[11,10,9,8,7])

    def test_follow_signal_affects_selection_without_reactions(self):
        for i in range(1,6): self.post(i,'A discussion from Bob.')
        for i in range(6,12): self.post(i,'A discussion from Carol.',user_id=3)
        self.follow(2)
        self.assertEqual(self.ids(),[5,4,3,2,1])

    def test_following_filter_is_strict(self):
        self.post(1,'woodworking timber workshop',user_id=3); self.react(1)
        self.post(2,'woodworking timber workshop',user_id=3)
        self.post(3,'violin orchestra concert',user_id=2)
        self.follow(2)
        self.assertEqual(self.ids(following=True),[3])
        self.assertEqual(self.ids(user_id=None,following=True),[])

    def test_no_follows_has_no_following_fallback(self):
        self.post(1,'A friendly discussion.')
        self.assertEqual(self.ids(following=True),[])

    def test_own_and_already_reacted_posts_are_excluded(self):
        self.post(1,'woodworking timber workshop',user_id=1)
        self.post(2,'woodworking timber workshop');self.react(2)
        self.post(3,'violin orchestra concert');self.react(3,'sad')
        self.post(4,'woodworking timber workshop')
        self.assertEqual(self.ids(),[4])

    def test_duplicate_signals_do_not_duplicate_recommendations(self):
        for i in range(1,8): self.post(i,'woodworking timber workshop')
        self.react(1);self.react(1);self.follow();self.follow()
        self.assertEqual(self.ids(),[7,6,5,4,3])

    def test_latest_reaction_wins_for_legacy_duplicates(self):
        self.post(1,'woodworking timber workshop');self.react(1);self.react(1,'angry')
        for i in range(2,7): self.post(i,'woodworking timber workshop')
        for i in range(7,12): self.post(i,'violin orchestra concert',user_id=3)
        self.assertEqual(self.ids(),[11,10,9,8,7])

    def test_empty_and_punctuation_only_text_do_not_crash(self):
        self.post(1,'');self.post(2,'123 !!!');self.react(1)
        self.assertEqual(self.ids(),[2])

    def test_live_follow_and_reaction_changes_recompute_selection(self):
        for i in range(1,6): self.post(i,'woodworking timber workshop')
        for i in range(6,11): self.post(i,'violin orchestra concert',user_id=3)
        self.assertEqual(self.ids(),[10,9,8,7,6])
        self.follow(2)
        self.assertEqual(self.ids(),[5,4,3,2,1])
        self.db.execute('DELETE FROM follows');self.db.commit()
        self.assertEqual(self.ids(),[10,9,8,7,6])

    def test_three_read_queries_and_no_writes(self):
        self.post(1,'woodworking timber workshop');self.post(2,'A music discussion.')
        statements=[];before=self.counts();self.db.set_trace_callback(statements.append)
        self.ids();self.db.set_trace_callback(None)
        self.assertEqual(sum(s.lstrip().upper().startswith('SELECT') for s in statements),3)
        self.assertFalse(any(s.lstrip().upper().startswith(('INSERT','UPDATE','DELETE')) for s in statements))
        self.assertEqual(before,self.counts())

    def test_recommended_route_has_no_pagination_and_escapes_text(self):
        self.post(1,'<script>alert(1)</script>');self.login()
        response=self.client.get('/?sort=recommended&page=99')
        self.assertEqual(response.status_code,200)
        self.assertIn(b'Recommended posts',response.data)
        self.assertIn(b'&lt;script&gt;',response.data)
        self.assertNotIn(b'<script>alert(1)</script>',response.data)
        self.assertNotIn(b'Next &raquo;',response.data)
        self.assertIn(b'/u/bob',response.data)


class IntroductionTests(DatabaseCase):
    def test_login_is_required(self):
        self.assertIn('/login',self.client.get('/introductions').location)
        self.assertIn('/login',self.client.post('/introductions',data={'content':'Hello!'}).location)
        self.assertEqual(self.counts()['posts'],0)

    def test_publishing_creates_one_public_thread_owned_by_session(self):
        self.login()
        response=self.client.post('/introductions',data={'content':'Hi, I enjoy woodworking.','user_id':'3'})
        self.assertEqual(response.status_code,302)
        post_id=own_introduction(self.db,1)['id']
        self.assertEqual(self.db.execute('SELECT user_id FROM posts WHERE id=?',(post_id,)).fetchone()[0],1)
        self.assertIsNone(own_introduction(self.db,3))
        self.assertIn(b'Hi, I enjoy woodworking.',self.client.get('/').data)
        self.assertIn(b'Introduction',self.client.get(f'/posts/{post_id}').data)

    def test_duplicate_submission_reuses_active_introduction(self):
        self.login()
        first=self.client.post('/introductions',data={'content':'Hi, I enjoy woodworking.'})
        second=self.client.post('/introductions',data={'content':'A second introduction.'})
        self.assertEqual(first.location,second.location)
        self.assertEqual(self.counts()['posts'],1)
        self.assertEqual(self.counts()['introductions'],1)

    def test_empty_or_long_introduction_does_not_publish(self):
        self.login()
        for content in ('  ','x'*1001):
            self.assertEqual(self.client.post('/introductions',data={'content':content}).status_code,400)
        self.assertEqual(self.counts()['posts'],0)

    def test_deleted_intro_can_be_recreated(self):
        self.login()
        self.client.post('/introductions',data={'content':'Hi, I enjoy woodworking.'})
        post_id=own_introduction(self.db,1)['id']
        self.client.post(f'/posts/{post_id}/delete')
        self.assertIsNone(own_introduction(self.db,1))
        self.client.post('/introductions',data={'content':'Hello again.'})
        self.assertEqual(self.counts()['posts'],1)
        self.assertEqual(self.counts()['introductions'],1)

    def test_metadata_failure_rolls_back_post(self):
        self.db.execute("CREATE TRIGGER fail_intro BEFORE INSERT ON introductions BEGIN SELECT RAISE(ABORT,'simulated failure'); END")
        self.db.commit()
        with self.assertRaises(sqlite3.IntegrityError):
            publish_introduction(self.db,1,'A failed introduction.')
        self.assertEqual(self.counts()['posts'],0)

    def test_concurrent_submissions_create_only_one_post(self):
        def publish(text):
            with sqlite3.connect(self.path) as db:
                db.row_factory=sqlite3.Row
                return publish_introduction(db,1,text)
        with ThreadPoolExecutor(max_workers=2) as pool:
            results=list(pool.map(publish,['Hello one.','Hello two.']))
        self.assertEqual(results[0][0],results[1][0])
        self.assertEqual(sum(created for _,created in results),1)
        self.assertEqual(self.counts()['posts'],1)

    def test_welcoming_reply_uses_existing_comment_flow(self):
        post_id,_=publish_introduction(self.db,1,'Hi, I enjoy woodworking.')
        self.login(2,'bob')
        self.assertIn(b'Say hello',self.client.get('/introductions').data)
        self.client.post(f'/posts/{post_id}/comment',data={'content':'Welcome, Alice! What are you building?'})
        self.assertIn(b'1 reply',self.client.get('/introductions').data)
        self.assertIn(b'Welcome, Alice!',self.client.get(f'/posts/{post_id}').data)

    def test_introductions_escape_user_text(self):
        self.login()
        self.client.post('/introductions',data={'content':'<script>alert(1)</script>'})
        response=self.client.get('/introductions')
        self.assertNotIn(b'<script>alert(1)</script>',response.data)
        self.assertIn(b'&lt;script&gt;',response.data)

    def test_signup_offers_optional_intro_and_skip(self):
        response=self.client.post('/signup',data={'username':'new_member','password':'test-password','profile':'A friendly introduction.'})
        self.assertEqual(response.location,'/introductions')
        self.assertEqual(self.counts()['introductions'],0)
        self.assertIn(b'Skip and browse posts',self.client.get('/introductions').data)


class PracticeTests(DatabaseCase):
    def test_login_required(self):
        for method in (self.client.get,self.client.post):
            self.assertIn('/login',method('/practice').location)

    def test_full_practice_flow_has_no_public_or_session_writes(self):
        self.login();before=self.counts()
        response=self.client.post('/practice',data={'action':'post','post_text':'What woodworking project should I try?'})
        self.assertIn(b'1/3 complete',response.data)
        response=self.client.post('/practice',data={'action':'react','post_text':'What woodworking project should I try?'})
        self.assertIn(b'2/3 complete',response.data)
        response=self.client.post('/practice',data={'action':'comment','post_text':'What woodworking project should I try?',
                                                  'comment_text':'A small shelf could be a good start.','reacted':'1'})
        self.assertIn(b'3/3 complete',response.data)
        self.assertIn(b'You have tried all three actions',response.data)
        self.assertEqual(before,self.counts())
        with self.client.session_transaction() as session:
            self.assertNotIn('woodworking',str(dict(session)))
        self.assertNotIn(b'What woodworking project should I try?',self.client.get('/').data)

    def test_unsubmitted_comment_stays_a_draft_when_reacting(self):
        self.login()
        response=self.client.post('/practice',data={'action':'react','post_text':'A practice question.',
                                                  'comment_text':'An unsent reply.'})
        self.assertIn(b'2/3 complete',response.data)
        self.assertNotIn(b'<strong>Your practice reply</strong>',response.data)

    def test_reaction_can_be_removed_without_losing_saved_reply(self):
        self.login()
        response=self.client.post('/practice',data={'action':'react','post_text':'A practice question.',
                     'saved_comment':'A saved practice reply.','comment_text':'A newer unsent draft.','reacted':'1'})
        self.assertIn(b'2/3 complete',response.data)
        self.assertIn(b'A saved practice reply.',response.data)
        self.assertIn(b'Like privately',response.data)

    def test_get_reset_clears_practice(self):
        self.login()
        self.client.post('/practice',data={'action':'post','post_text':'My unique practice draft.'})
        response=self.client.get('/practice')
        self.assertIn(b'0/3 complete',response.data)
        self.assertNotIn(b'My unique practice draft.',response.data)

    def test_invalid_empty_or_long_actions_do_not_write(self):
        self.login();before=self.counts()
        for data in ({'action':'publish','post_text':'An invalid action.'},
                     {'action':'post','post_text':' '},
                     {'action':'post','post_text':'x'*1001},
                     {'action':'comment','post_text':'A post.','comment_text':''}):
            self.assertEqual(self.client.post('/practice',data=data).status_code,400)
        self.assertEqual(before,self.counts())

    def test_practice_escapes_preview_text_and_hidden_fields(self):
        self.login()
        response=self.client.post('/practice',data={'action':'post','post_text':'<script>alert(1)</script> "hello"'})
        self.assertNotIn(b'<script>alert(1)</script>',response.data)
        self.assertIn(b'&lt;script&gt;',response.data)
        self.assertIn(b'&#34;hello&#34;',response.data)


if __name__ == '__main__':
    unittest.main()
