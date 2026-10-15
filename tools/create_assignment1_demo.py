"""Create a separate, small dataset for demonstrating Assignment 1.

Run from the repository root. Existing files are never overwritten, and the
provided database.sqlite is opened read-only to copy its table definitions.
"""

import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sqlite3

from werkzeug.security import generate_password_hash


ROOT = Path(__file__).resolve().parents[1]


def create_demo(destination):
    destination = destination.resolve()
    if destination.exists():
        raise FileExistsError(f'{destination} already exists; choose a new --output path.')
    destination.parent.mkdir(parents=True, exist_ok=True)
    source_uri = (ROOT / 'database.sqlite').as_uri() + '?mode=ro'
    with sqlite3.connect(source_uri, uri=True) as source:
        tables = source.execute(
            "SELECT sql FROM sqlite_master WHERE type = 'table' AND name != 'sqlite_sequence'"
        ).fetchall()

    now = datetime.now(timezone.utc)
    current = now.strftime('%Y-%m-%d %H:%M:%S')
    older = (now - timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')
    password = generate_password_hash('demo-password')
    with sqlite3.connect(destination) as db:
        for (schema,) in tables:
            db.execute(schema)
        db.executemany(
            'INSERT INTO users (id, username, password, profile) VALUES (?, ?, ?, ?)',
            [(1, 'demo_alice', password, 'Learning together, one conversation at a time.'),
             (2, 'demo_bob', password, 'Sharing questions and study tips.'),
             (3, 'demo_carol', password, 'Interested in building better online communities.')],
        )
        db.executemany(
            'INSERT INTO posts (id, user_id, content, created_at) VALUES (?, ?, ?, ?)',
            [(1, 1, 'What helps you feel welcome in an online study group?', older),
             (2, 3, 'What is one thing you learned about community commitment?', current),
             (3, 3, 'How do you encourage quieter members to join a discussion?', current),
             (4, 2, 'Any tips for making a first contribution less intimidating?', current),
             (5, 3, 'What makes a comment useful to you?', current),
             (6, 2, 'What is a good way to thank someone who helped you?', current),
             (7, 1, 'I would love to hear your examples of welcoming communities.', current)],
        )
        db.executemany(
            'INSERT INTO comments (post_id, user_id, content, created_at) VALUES (?, ?, ?, ?)',
            [(2, 1, 'Knowing the people behind the posts helps me keep coming back.', current),
             (3, 1, 'Ask a specific question that is easy to respond to.', current),
             (1, 2, 'A friendly response to my first post makes a big difference.', current),
             (1, 3, 'Shared goals help me feel part of the group.', current)],
        )
        db.commit()
    print(f'Demo database: {destination}')
    print('Accounts: demo_alice, demo_bob, demo_carol. Password: demo-password')
    print('Alice starts at 2/3 posts. Reply to Bob to complete her weekly goal.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / '.local-data' / 'assignment1.sqlite')
    arguments = parser.parse_args()
    try:
        create_demo(arguments.output)
    except FileExistsError as error:
        parser.exit(1, f'{error}\n')
