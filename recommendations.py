"""Small content-based recommender using existing posts, reactions and follows.

No model service or extra package is needed. Rank by TF-IDF cosine similarity
and a followed-author bonus, select five, then present that set newest first.
"""
from collections import Counter, defaultdict
from math import log, sqrt
import re

POSITIVE_REACTIONS = {'like', 'love', 'laugh', 'haha', 'wow'}
FOLLOW_BONUS = 0.35
STOP_WORDS = set('''a about after again all also am an and any are as at be because
been before being between both but by can could did do does doing down each even
few for from further get got had has have having he her here hers herself him
himself his how i if in into is it its itself just like me more most my myself no
nor not of off on once only or other our ours ourselves out over own same she
should so some such than that the their theirs them themselves then there these
they this those through to too under until up very was we were what when where
which while who whom why will with would you your yours yourself yourselves'''.split())


def _tokens(text):
    return Counter(word for word in re.findall(r'[^\W\d_]{2,}', (text or '').casefold())
                   if word not in STOP_WORDS)


def _unit(vector):
    length = sqrt(sum(value * value for value in vector.values()))
    return {term: value / length for term, value in vector.items()} if length else {}


def recommended_posts(db, user_id, filter_following=False):
    """Read the current signals in at most three queries; never write data.

    Positive reactions build a normalized interest vector. The latest reaction
    wins if legacy data has duplicate rows. Own and already-reacted posts are
    excluded. Following is a strict filter; cold-start ties use recency and ID.
    """
    if filter_following and not user_id:
        return []
    posts = [dict(row) for row in db.execute('''
        SELECT p.id, p.user_id, p.content, p.created_at, u.username
        FROM posts p JOIN users u ON u.id=p.user_id
        ORDER BY p.created_at DESC, p.id DESC
    ''')]
    reactions = {}
    followed = set()
    if user_id:
        for row in db.execute('SELECT post_id,reaction_type FROM reactions WHERE user_id=? ORDER BY id DESC', (user_id,)):
            reactions.setdefault(row['post_id'], row['reaction_type'])
        followed = {row['followed_id'] for row in db.execute('SELECT followed_id FROM follows WHERE follower_id=?', (user_id,))}

    counts = {post['id']: _tokens(post['content']) for post in posts}
    frequency = Counter(term for words in counts.values() for term in words)
    idf = {term: 1 + log((1 + len(posts)) / (1 + count)) for term, count in frequency.items()}
    vectors = {post_id: _unit({term: (1 + log(count)) * idf[term] for term, count in words.items()})
               for post_id, words in counts.items()}
    interest = defaultdict(float)
    for post in posts:
        if post['user_id'] != user_id and reactions.get(post['id']) in POSITIVE_REACTIONS:
            for term, value in vectors[post['id']].items():
                interest[term] += value
    interest = _unit(interest)

    ranked = []
    for post in posts:
        if post['user_id'] == user_id or post['id'] in reactions:
            continue
        is_followed = post['user_id'] in followed
        if filter_following and not is_followed:
            continue
        similarity = sum(value * interest.get(term, 0.0) for term, value in vectors[post['id']].items())
        score = similarity + (FOLLOW_BONUS if is_followed else 0.0)
        if similarity > 0 and is_followed:
            reason = 'From someone you follow and similar to posts you enjoyed.'
        elif is_followed:
            reason = 'From someone you follow.'
        elif similarity > 0:
            reason = 'Similar to posts you enjoyed.'
        else:
            reason = 'A recent post to help you explore.'
        post['recommendation_reason'] = reason
        ranked.append((score, post))
    # Stable ties are resolved by timestamp and ID, including posts in one second.
    ranked.sort(key=lambda item: (item[0], str(item[1]['created_at'] or ''), item[1]['id']), reverse=True)
    selected = [post for _, post in ranked[:5]]
    selected.sort(key=lambda post: (str(post['created_at'] or ''), post['id']), reverse=True)
    return selected
