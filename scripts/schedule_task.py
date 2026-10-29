#!/usr/bin/env python3
"""Schedule repeating tasks using your system's built-in scheduler.

On Mac/Linux this works with cron (crontab). On Windows it prints the
equivalent Task Scheduler (schtasks) command so you can set it up yourself.

Safety first: defaults to dry-run (prints what it would do, changes nothing).
Pass --apply to actually write to your crontab (a backup is made first).
Only touches your own user crontab. Standard library only.
"""

import os
import subprocess
import sys

CRON_NOTE = ("If cron is not available (e.g. Windows), use Task Scheduler "
             "(schtasks) instead. See docs/scheduling.md.")


def make_cron_line(schedule, command):
    """Build a single crontab line: schedule + command."""
    return f"{schedule} {command}\n"


def parse_cron_line(line):
    """Parse a crontab line into (schedule, command) or None if not a job."""
    line = line.strip()
    if not line or line.startswith("#"):
        return None
    parts = line.split(None, 5)
    if len(parts) < 6:
        return None
    schedule = " ".join(parts[:5])
    command = parts[5]
    return schedule, command


def cron_lines_in(text):
    """Return the list of job lines (schedule, command) in crontab text."""
    jobs = []
    for line in text.splitlines():
        parsed = parse_cron_line(line)
        if parsed is not None:
            jobs.append(parsed)
    return jobs


def add_job(lines, schedule, command):
    """Add a job line to a list of crontab lines if not already present."""
    for sched, cmd in lines:
        if sched == schedule and cmd == command:
            return lines  # already present, no duplicate
    return lines + [(schedule, command)]


def remove_job(lines, command):
    """Remove job lines whose command matches. Returns (new_lines, removed)."""
    new_lines = [(sched, cmd) for sched, cmd in lines if cmd != command]
    removed = len(lines) - len(new_lines)
    return new_lines, removed


def read_crontab():
    """Read the current user crontab. Returns "" if none exists."""
    try:
        result = subprocess.run(["crontab", "-l"], capture_output=True,
                                text=True, timeout=15)
        if result.returncode != 0:
            return ""
        return result.stdout
    except FileNotFoundError:
        print("Note: `crontab` not found on this system. " + CRON_NOTE,
              file=sys.stderr)
        return ""
    except Exception as exc:  # noqa: BLE001 - report and continue
        print(f"Warning: could not read crontab: {exc}", file=sys.stderr)
        return ""


def write_crontab(text):
    """Write text to the user crontab, backing up the current one first."""
    backup = read_crontab()
    if backup:
        backup_path = os.path.expanduser("~/.crontab.backup")
        with open(backup_path, "w", encoding="utf-8") as fh:
            fh.write(backup)
    proc = subprocess.run(["crontab", "-"], input=text, text=True,
                          capture_output=True, timeout=15)
    if proc.returncode != 0:
        print(f"Error: crontab write failed: {proc.stderr}", file=sys.stderr)
        return 1
    return 0


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)

    apply_flag = False
    action = None
    schedule = None
    command = None

    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg in ("--apply", "-a"):
            apply_flag = True
        elif arg == "--list" or arg == "-l":
            action = "list"
        elif arg == "--add" and i + 2 < len(argv):
            action = "add"
            schedule = argv[i + 1]
            command = argv[i + 2]
            i += 2
        elif arg == "--remove" and i + 1 < len(argv):
            action = "remove"
            command = argv[i + 1]
            i += 1
        elif arg == "--help" or arg == "-h":
            print_usage()
            return 0
        else:
            print(f"Error: unknown option or bad args: {arg}", file=sys.stderr)
            return 1
        i += 1

    if action is None:
        print("Error: an action is required (--list, --add, --remove).",
              file=sys.stderr)
        print_usage()
        return 1

    current = read_crontab()
    lines = cron_lines_in(current)

    if action == "list":
        if not lines:
            print("No cron jobs found in your crontab.")
        else:
            print("Your cron jobs:")
            for sched, cmd in lines:
                print(f"  {sched}  {cmd}")
        return 0

    if action == "add":
        new_lines = add_job(lines, schedule, command)
        crontab_text = _build_crontab_text(current, new_lines)
        if apply_flag:
            return write_crontab(crontab_text)
        print("[dry-run] Would add this cron job:")
        print(f"    {schedule}  {command}")
        print("\nPass --apply to write it to your crontab.")
        return 0

    if action == "remove":
        new_lines, removed = remove_job(lines, command)
        if removed == 0:
            print(f"No cron job matching command: {command}")
            return 0
        crontab_text = _build_crontab_text(current, new_lines)
        if apply_flag:
            return write_crontab(crontab_text)
        print(f"[dry-run] Would remove {removed} job(s) matching: {command}")
        print("\nPass --apply to remove it from your crontab.")
        return 0

    return 0


def _build_crontab_text(current, new_lines):
    """Rebuild crontab text preserving non-job lines (comments, vars)."""
    kept = []
    for line in current.splitlines():
        if parse_cron_line(line) is None:
            kept.append(line)
    for sched, cmd in new_lines:
        kept.append(make_cron_line(sched, cmd).rstrip("\n"))
    return "\n".join(kept) + ("\n" if kept else "")


def print_usage():
    print("Usage: python3 schedule_task.py --list [--apply]",
          file=sys.stderr)
    print("       python3 schedule_task.py --add <schedule> <command> [--apply]",
          file=sys.stderr)
    print("       python3 schedule_task.py --remove <command> [--apply]",
          file=sys.stderr)
    print("\n<schedule> is a cron schedule, e.g. '*/15 * * * *' (every 15 min).")
    print("Defaults to dry-run: prints changes, writes nothing.")
    print("\nOptions:")
    print("  --list     Show your current cron jobs (read-only)")
    print("  --add      Add a cron job (schedule + command)")
    print("  --remove   Remove cron jobs matching a command")
    print("  --apply    Write changes to crontab (backup made first)")
    print("\nSafety: preview first, then add --apply. Only your own crontab is touched.")
    print("Example: python3 scripts/schedule_task.py --add '*/15 * * * *' "
          "'python3 my_backup.py' --apply")
