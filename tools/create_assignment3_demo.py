"""Seed a separate newcomer/recommendation demo without changing course data."""
import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sqlite3
import sys
from werkzeug.security import generate_password_hash

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from newcomers import ensure_schema


def create_demo(destination):
    destination = destination.resolve()
    if destination.exists():
        raise FileExistsError(f'{destination} exists; choose another --output filename.')
    destination.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect((ROOT/'database.sqlite').as_uri()+'?mode=ro', uri=True) as source:
        tables=source.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name!='sqlite_sequence'").fetchall()
    now=datetime.now(timezone.utc)
    old=(now-timedelta(days=40)).strftime('%Y-%m-%d %H:%M:%S')
    recent=now.strftime('%Y-%m-%d %H:%M:%S')
    password=generate_password_hash('demo-password')
    with sqlite3.connect(destination) as db:
        for (schema,) in tables: db.execute(schema)
        ensure_schema(db)
        db.executemany('INSERT INTO users(id,username,password,profile,created_at) VALUES(?,?,?,?,?)',[
            (1,'demo_alice',password,'New here and finding my interests.',recent),
            (2,'demo_bob',password,'I enjoy DIY woodworking and helping people get started.',old),
            (3,'demo_carol',password,'Sharing DIY projects and workshop tips.',old),
            (4,'demo_dave',password,'I enjoy films and meeting new people.',recent),
        ])
        posts=[
            (1,2,'DIY woodworking: a beginner workshop project using timber and simple tools.'),
            (2,2,'DIY woodworking: build a timber shelf with simple workshop tools.'),
            (3,2,'DIY woodworking: choosing timber and tools for a weekend workshop project.'),
            (4,2,'DIY woodworking: a small timber planter is a friendly first workshop project.'),
            (5,3,'DIY woodworking: how do you organise your timber and workshop tools?'),
            (6,3,'DIY woodworking: show us a simple timber project from your workshop.'),
            (7,4,'Which film soundtrack should a new cinema fan listen to?'),
            (8,4,'A conversation about cinema, directors and the latest film releases.'),
            (9,4,'What makes a film worth watching twice at the cinema?'),
            (10,4,'What is your favourite cinema snack during a long film?'),
            (11,4,'Let us discuss memorable cinema scenes and film soundtracks.'),
            (12,4,'Who is your favourite film director and why?'),
            (13,4,'Hi everyone! I enjoy films and would love to meet other cinema fans.'),
        ]
        db.executemany('INSERT INTO posts(id,user_id,content,created_at) VALUES(?,?,?,?)',
                       [(pid,uid,text,(now-timedelta(minutes=30-pid)).strftime('%Y-%m-%d %H:%M:%S')) for pid,uid,text in posts])
        db.execute('INSERT INTO introductions(user_id,post_id) VALUES(4,13)')
    print(f'Demo database: {destination}')
    print('Accounts: demo_alice, demo_bob, demo_carol, demo_dave; password: demo-password')
    print('Alice starts without reactions or follows. Like post 1 and follow Bob to personalise her recommendations.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'.local-data'/'assignment3.sqlite')
    create_demo(parser.parse_args().output)
