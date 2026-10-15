"""Read-only summaries for Coding Assignment 1's three Design Claims."""

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo


COMMUNITY_TIMEZONE = ZoneInfo("Europe/Helsinki")
WEEKLY_GOAL = 3


def community_week(now=None):
    """Return a Helsinki calendar week and UTC bounds for SQLite timestamps.

    SQLite CURRENT_TIMESTAMP stores UTC without a timezone suffix. Converting
    each local boundary separately also handles weeks that cross a DST change.
    """
    now = now if now is not None else datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError("now must be timezone-aware")
    local_now = now.astimezone(COMMUNITY_TIMEZONE)
    start = local_now.replace(hour=0, minute=0, second=0, microsecond=0)
    start -= timedelta(days=start.weekday())
    end = start + timedelta(days=7)
    return {
        "start": start,
        "end": end,
        "last_day": (end - timedelta(days=1)).date(),
        "start_utc": start.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "end_utc": end.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
    }


def weekly_goal_progress(db, user_id, week):
    """Count distinct other people's posts replied to during this week.

    Derive progress from comments instead of keeping a separate counter, so
    duplicate comments cannot inflate it and removed comments no longer count.
    """
    row = db.execute(
        """
        SELECT COUNT(DISTINCT c.post_id) AS completed
        FROM comments c
        JOIN posts p ON p.id = c.post_id
        WHERE c.user_id = ? AND p.user_id != ?
          AND c.created_at >= ? AND c.created_at < ?
        """,
        (user_id, user_id, week["start_utc"], week["end_utc"]),
    ).fetchone()
    completed = row["completed"]
    return {
        "completed": completed,
        "target": WEEKLY_GOAL,
        "display_completed": min(completed, WEEKLY_GOAL),
        "percent": min(100, completed * 100 // WEEKLY_GOAL),
        "achieved": completed >= WEEKLY_GOAL,
    }


def contribution_dashboard(db, user_id, now=None):
    """Build visible opportunities, goal feedback, and received-support data."""
    week = community_week(now)

    # Chapter 2, Claim 1: make contributions needed by others visible.
    needs_reply = db.execute(
        """
        SELECT p.id, p.content, p.created_at, u.username
        FROM posts p
        JOIN users u ON u.id = p.user_id
        WHERE p.user_id != ?
          AND NOT EXISTS (SELECT 1 FROM comments c WHERE c.post_id = p.id)
        ORDER BY p.created_at DESC, p.id DESC
        LIMIT 5
        """,
        (user_id,),
    ).fetchall()

    # Chapter 3, Claim 30: show what the member has received from others.
    support_args = (user_id, user_id, week["start_utc"], week["end_utc"])
    support = db.execute(
        """
        SELECT COUNT(*) AS comments, COUNT(DISTINCT c.user_id) AS members
        FROM comments c
        JOIN posts p ON p.id = c.post_id
        JOIN users u ON u.id = c.user_id
        WHERE p.user_id = ? AND c.user_id != ?
          AND c.created_at >= ? AND c.created_at < ?
        """,
        support_args,
    ).fetchone()
    recent_support = db.execute(
        """
        SELECT c.id, c.post_id, c.content, c.created_at, u.username
        FROM comments c
        JOIN posts p ON p.id = c.post_id
        JOIN users u ON u.id = c.user_id
        WHERE p.user_id = ? AND c.user_id != ?
          AND c.created_at >= ? AND c.created_at < ?
        ORDER BY c.created_at DESC, c.id DESC
        LIMIT 3
        """,
        support_args,
    ).fetchall()

    return {
        "week": week,
        "needs_reply": [dict(post) for post in needs_reply],
        # Chapter 2, Claim 15: frequent feedback about a specific goal.
        "goal": weekly_goal_progress(db, user_id, week),
        "support": dict(support),
        "recent_support": [dict(comment) for comment in recent_support],
    }
