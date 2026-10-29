#!/usr/bin/env python3
"""Tests for schedule_task.py.

Run: python3 tests/test_schedule_task.py
(No system crontab is touched.)
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import schedule_task  # noqa: E402


def test_make_and_parse_cron_line():
    line = schedule_task.make_cron_line("*/15 * * * *", "python3 backup.py")
    assert line == "*/15 * * * * python3 backup.py\n"
    parsed = schedule_task.parse_cron_line(line)
    assert parsed == ("*/15 * * * *", "python3 backup.py")


def test_cron_lines_in_skips_comments_and_empties():
    text = "# my crontab\nSHELL=/bin/bash\n\n*/15 * * * * python3 backup.py\n# another\n0 2 * * * python3 cleanup.py\n"
    jobs = schedule_task.cron_lines_in(text)
    assert jobs == [
        ("*/15 * * * *", "python3 backup.py"),
        ("0 2 * * *", "python3 cleanup.py"),
    ]


def test_add_job_avoids_duplicates():
    lines = [("0 2 * * *", "python3 cleanup.py")]
    result = schedule_task.add_job(lines, "0 2 * * *", "python3 cleanup.py")
    assert result == lines  # no duplicate added
    result = schedule_task.add_job(lines, "*/15 * * * *", "python3 backup.py")
    assert ("*/15 * * * *", "python3 backup.py") in result


def test_remove_job():
    lines = [
        ("0 2 * * *", "python3 cleanup.py"),
        ("*/15 * * * *", "python3 backup.py"),
        ("0 2 * * *", "python3 cleanup.py"),  # duplicate command
    ]
    new_lines, removed = schedule_task.remove_job(lines, "python3 cleanup.py")
    assert removed == 2
    assert all(cmd != "python3 cleanup.py" for _, cmd in new_lines)
    assert ("*/15 * * * *", "python3 backup.py") in new_lines


def test_read_crontab_returns_string():
    # Should not crash; returns current crontab text or "" if none.
    text = schedule_task.read_crontab()
    assert isinstance(text, str)


if __name__ == "__main__":
    test_make_and_parse_cron_line()
    test_cron_lines_in_skips_comments_and_empties()
    test_add_job_avoids_duplicates()
    test_remove_job()
    test_read_crontab_returns_string()
    print("All schedule_task tests passed.")
