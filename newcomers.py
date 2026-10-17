"""Introduction metadata and transactions for Chapter 5, Design Claim 19."""


def ensure_schema(db):
    """Add metadata without changing the supplied user/post table definitions."""
    db.execute('''CREATE TABLE IF NOT EXISTS introductions (
        user_id INTEGER PRIMARY KEY,
        post_id INTEGER NOT NULL UNIQUE,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (post_id) REFERENCES posts(id)
    )''')
    db.commit()


def own_introduction(db, user_id):
    # The join tolerates introductions deleted using the original course tools.
    return db.execute('''SELECT p.id FROM introductions i
        JOIN posts p ON p.id=i.post_id AND p.user_id=i.user_id
        WHERE i.user_id=?''', (user_id,)).fetchone()


def publish_introduction(db, user_id, content):
    """Create the real post and metadata together; repeat clicks reuse the post."""
    with db:
        # Serialize the check/insert so two simultaneous submissions cannot
        # leave an unmarked duplicate post behind.
        db.execute('BEGIN IMMEDIATE')
        existing = own_introduction(db, user_id)
        if existing:
            return existing['id'], False
        cursor = db.execute('INSERT INTO posts(user_id,content) VALUES(?,?)', (user_id, content))
        post_id = cursor.lastrowid
        db.execute('''INSERT INTO introductions(user_id,post_id) VALUES(?,?)
            ON CONFLICT(user_id) DO UPDATE SET post_id=excluded.post_id''', (user_id, post_id))
    return post_id, True


def recent_introductions(db, limit=10):
    return [dict(row) for row in db.execute('''
        SELECT p.id,p.user_id,p.content,p.created_at,u.username,
               (SELECT COUNT(*) FROM comments c WHERE c.post_id=p.id) AS reply_count
        FROM introductions i JOIN posts p ON p.id=i.post_id AND p.user_id=i.user_id
        JOIN users u ON u.id=i.user_id
        ORDER BY p.created_at DESC,p.id DESC LIMIT ?
    ''', (limit,))]
