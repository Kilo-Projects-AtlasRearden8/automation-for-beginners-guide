#!/usr/bin/env python3
"""Tests for repeat_task.py.

Run: python3 tests/test_repeat_task.py
"""

import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import repeat_task  # noqa: E402


def test_dry_run_prints_schedule_without_running():
    original_run_once = repeat_task.run_once
    calls = []
    repeat_task.run_once = lambda command: calls.append(command)  # noqa

    try:
        ns = repeat_task.parse_args(["echo hi", "--every", "10", "--times", "3"])
        assert ns["apply"] is False
        assert ns["every"] == 10
        assert ns["times"] == 3
        assert ns["command"] == "echo hi"

        repeat_task.repeat(ns["command"], ns["every"], ns["times"], ns["apply"])
        assert calls == []  # nothing executed in dry-run
    finally:
        repeat_task.run_once = original_run_once


def test_apply_runs_command_once():
    marker = os.path.join(tempfile.mkdtemp(), "ran.txt")
    cmd = f"python3 -c \"open('{marker}', 'w').write('x')\""

    ns = repeat_task.parse_args([cmd, "--every", "1", "--times", "1",
                                 "--apply"])
    assert ns["apply"] is True

    repeat_task.repeat(ns["command"], ns["every"], ns["times"], ns["apply"])
    assert os.path.isfile(marker)


def test_parse_every_validation():
    assert repeat_task.parse_args(["echo x", "--every", "60"])["every"] == 60
    assert repeat_task.parse_args(["echo x", "--every", "1"])["every"] == 1
    assert repeat_task.parse_args(["echo x", "--every", "60",
                                   "--times", "5"])["times"] == 5
    assert repeat_task.parse_args(["echo x"])["times"] is None
    assert repeat_task.parse_args(["echo x"])["apply"] is False


if __name__ == "__main__":
    test_dry_run_prints_schedule_without_running()
    test_apply_runs_command_once()
    test_parse_every_validation()
    print("All repeat_task tests passed.")
