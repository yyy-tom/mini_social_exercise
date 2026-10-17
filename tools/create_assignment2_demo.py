"""Create a small, separate Assignment 2 demo; never overwrite an existing file."""
import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sqlite3
from werkzeug.security import generate_password_hash

ROOT = Path(__file__).resolve().parents[1]


def create_demo(destination):
    destination = destination.resolve()
    if destination.exists():
        raise FileExistsError(f'{destination} exists; choose a fresh --output path.')
    destination.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect((ROOT / 'database.sqlite').as_uri() + '?mode=ro', uri=True) as source:
        tables = source.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name!='sqlite_sequence'").fetchall()
    now = datetime.now(timezone.utc)
    old = (now - timedelta(days=40)).strftime('%Y-%m-%d %H:%M:%S')
    recent = now.strftime('%Y-%m-%d %H:%M:%S')
    password = generate_password_hash('demo-password')
    with sqlite3.connect(destination) as db:
        for (schema,) in tables:
            db.execute(schema)
        db.executemany('INSERT INTO users(id,username,password,profile,created_at) VALUES(?,?,?,?,?)', [
            (1, 'admin', generate_password_hash('admin'), 'Demo moderator.', old),
            (2, 'demo_alice', password, 'Learning about moderation. tier3badword', old),
            (3, 'demo_bob', password, 'A new member of the study group.', recent),
            (4, 'demo_carol', password, 'tier1badword', old),
        ])
        db.executemany('INSERT INTO posts(id,user_id,content,created_at) VALUES(?,?,?,?)', [
            (1, 3, 'How can we keep discussions friendly when we disagree?', recent),
            (2, 4, 'This is a safe test token: tier1badword', old),
            (3, 4, 'This is another safe test token: tier2badword', old),
        ])
        db.execute('INSERT INTO comments(post_id,user_id,content,created_at) VALUES(1,3,?,?)',
                   ('A demonstration of mild-word masking: tier3badword', recent))
    print(f'Demo database: {destination}')
    print('Member login: demo_alice / demo-password. Moderator: admin / admin.')
    print('Initial user scores: Alice 2.0 LOW, Bob 3.0 MEDIUM, Carol 5.0 HIGH.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / '.local-data' / 'assignment2.sqlite')
    create_demo(parser.parse_args().output)
