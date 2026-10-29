#!/usr/bin/env python3
"""Repeat a command at a fixed interval.

Safety first: defaults to dry-run (prints the schedule, runs nothing). Pass
--apply to actually execute the command. Nothing is moved, deleted, or sent
anywhere. Standard library only.

Examples:
    python3 scripts/repeat_task.py "echo hello" --every 10 --times 3
    python3 scripts/repeat_task.py "python3 my_backup.py" --every 3600 --apply
"""

import shlex
import subprocess
import sys
import time


def parse_args(argv):
    """Parse command-line args into a small namespace dict."""
    ns = {
        "command": None,
        "every": 60,
        "times": None,
        "apply": False,
    }

    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg in ("--apply", "-a"):
            ns["apply"] = True
        elif arg == "--every" and i + 1 < len(argv):
            try:
                ns["every"] = int(argv[i + 1])
            except ValueError:
                print(f"Error: --every must be a number, got: {argv[i + 1]}",
                      file=sys.stderr)
                return None
            i += 1
        elif arg == "--times" and i + 1 < len(argv):
            try:
                ns["times"] = int(argv[i + 1])
            except ValueError:
                print(f"Error: --times must be a number, got: {argv[i + 1]}",
                      file=sys.stderr)
                return None
            i += 1
        elif arg == "--help" or arg == "-h":
            print_usage()
            return "help"
        elif not arg.startswith("-"):
            ns["command"] = arg
        else:
            print(f"Error: unknown option: {arg}", file=sys.stderr)
            return None
        i += 1

    if ns["command"] is None:
        print("Error: a command is required.", file=sys.stderr)
        print_usage()
        return None

    if ns["every"] < 1:
        print("Error: --every must be at least 1 second.", file=sys.stderr)
        return None

    return ns


def print_usage():
    print("Usage: python3 repeat_task.py <command> --every N [--times M] [--apply]",
          file=sys.stderr)
    print("\nRuns <command> every N seconds, up to M times (forever if omitted).")
    print("Defaults to dry-run: it prints the schedule without running anything.")
    print("\nOptions:")
    print("  --every N    Seconds between runs (default 60)")
    print("  --times M    Stop after M runs (default: repeat forever)")
    print("  --apply      Run the command for real (default is preview only)")
    print("\nSafety: preview first, then add --apply. Test with a harmless command.")
    print("Example: python3 scripts/repeat_task.py 'echo hello' --every 10 --times 3")


def run_once(command):
    """Run a single shell command, returning its return code."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True,
                                text=True, timeout=60)
        if result.stdout:
            print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, end="", file=sys.stderr)
        return result.returncode
    except subprocess.TimeoutExpired:
        print("Error: command timed out after 60 seconds.", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001 - report and keep going
        print(f"Error: could not run command: {exc}", file=sys.stderr)
        return 1


def repeat(command, every, times, apply):
    """Run `command` every `every` seconds, up to `times` times."""
    if not apply:
        print("[dry-run] Would run:")
        print(f"    {command}")
        print(f"    every {every} second(s)")
        if times is not None:
            print(f"    {times} time(s), then stop")
        else:
            print("    forever (press Ctrl-C to stop)")
        print("\nPass --apply to run for real.")
        return 0

    count = 0
    try:
        while True:
            if times is not None and count >= times:
                break
            count += 1
            label = f"run {count}" if times is None else f"run {count}/{times}"
            print(f"[{label}] executing: {command}")
            run_once(command)
            if times is not None and count >= times:
                break
            print(f"Waiting {every} second(s) before next run "
                  "(Ctrl-C to stop)...")
            time.sleep(every)
    except KeyboardInterrupt:
        print("\nStopped by user.")
    print(f"\nDone. {count} run(s) completed.")
    return 0


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    ns = parse_args(argv)
    if ns is None:
        return 1
    if ns == "help":
        return 0
    return repeat(ns["command"], ns["every"], ns["times"], ns["apply"])


if __name__ == "__main__":
    sys.exit(main())
