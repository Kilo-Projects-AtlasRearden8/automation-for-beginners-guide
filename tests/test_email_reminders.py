#!/usr/bin/env python3
"""Tests for email_reminders.py.

Run: python3 tests/test_email_reminders.py
"""

import os
import sys
import tempfile
from datetime import date, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import email_reminders  # noqa: E402


def write_reminders(tmp, lines):
    path = os.path.join(tmp, "reminders.txt")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    return path


def test_parse_reminders():
    tmp = tempfile.mkdtemp()
    try:
        today = date.today()
        soon = (today + timedelta(days=2)).isoformat()
        late = (today - timedelta(days=1)).isoformat()
        path = write_reminders(tmp, [
            "# comment",
            "Electric | " + soon + " | Pay electric",
            "Rent | " + late + " | Pay rent",
            "bad | not-a-date | x",  # skipped
            "Incomplete | 2026-11-05",  # skipped (<3 parts)
        ])
        reminders = email_reminders.parse_reminders(path)
        names = [r[0] for r in reminders]
        assert "Electric" in names
        assert "Rent" in names
        assert "bad" not in names
        assert "Incomplete" not in names
    finally:
        import shutil
        shutil.rmtree(tmp)


def test_categorize():
    today = date.today()
    reminders = [
        ("A", today, "msg A", 1),
        ("B", today + timedelta(days=3), "msg B", 2),
        ("C", today + timedelta(days=30), "msg C", 3),
        ("D", today - timedelta(days=2), "msg D", 4),
    ]
    due_today, upcoming, overdue = email_reminders.categorize(
        reminders, today, within_days=7)
    assert [r[0] for r in due_today] == ["A"]
    assert [r[0] for r in upcoming] == ["B"]
    assert [r[0] for r in overdue] == ["D"]


def test_dry_run_prints_and_sends_nothing():
    tmp = tempfile.mkdtemp()
    try:
        today = date.today()
        soon = (today + timedelta(days=1)).isoformat()
        path = write_reminders(tmp, ["Reminder | " + soon + " | Do it"])
        # Should run without crashing and not send (dry-run default).
        email_reminders.check_reminders(path, within_days=7, today=today,
                                        dry_run=True)
    finally:
        import shutil
        shutil.rmtree(tmp)


if __name__ == "__main__":
    test_parse_reminders()
    test_categorize()
    test_dry_run_prints_and_sends_nothing()
    print("All email_reminders tests passed.")
