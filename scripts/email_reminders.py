#!/usr/bin/env python3
"""Email reminders from a local reminders file.

Reads reminders.txt (name | due date YYYY-MM-DD | message) and renders the
email you'd send for each one. Defaults to dry-run: prints the email content
and a mailto: link, sends nothing. With --apply and SMTP environment variables
(set in your shell, never in this file) it can send for real via smtplib.

Standard library only. No credentials, API keys, or personal data are stored
in this script or the repo.
"""

import os
import sys
from datetime import date, timedelta

REMINDER_LINE = "name | due date (YYYY-MM-DD) | message"

# Environment variables used only when --apply is passed. Never hardcoded.
SMTP_HOST = os.environ.get("SMTP_HOST")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587") or 587)
SMTP_USER = os.environ.get("SMTP_USER")
SMTP_PASS = os.environ.get("SMTP_PASS")
FROM_EMAIL = os.environ.get("FROM_EMAIL")
TO_EMAIL = os.environ.get("TO_EMAIL")


def parse_reminders(path):
    """Parse reminders.txt into a list of (name, due_date, message, line_no)."""
    reminders = []
    with open(path, "r", encoding="utf-8") as fh:
        for line_no, raw in enumerate(fh, start=1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            parts = [p.strip() for p in line.split("|")]
            if len(parts) < 3:
                print(f"Warning: skipping malformed line {line_no}: {raw.rstrip()}",
                      file=sys.stderr)
                continue
            name, due_str, message = parts[0], parts[1], "|".join(parts[2:]).strip()
            try:
                due_date = date.fromisoformat(due_str)
            except ValueError:
                print(f"Warning: bad date on line {line_no}: {due_str}",
                      file=sys.stderr)
                continue
            reminders.append((name, due_date, message, line_no))
    return reminders


def categorize(reminders, today, within_days=7):
    """Split reminders into due today, upcoming, and overdue lists."""
    limit = today + timedelta(days=within_days)
    due_today, upcoming, overdue = [], [], []
    for name, due_date, message, line_no in reminders:
        if due_date == today:
            due_today.append((name, due_date, message, line_no))
        elif due_date < today:
            overdue.append((name, due_date, message, (today - due_date).days,
                            line_no))
        elif due_date <= limit:
            upcoming.append((name, due_date, message, (due_date - today).days,
                             line_no))
    return due_today, upcoming, overdue


def mailto(name, message, due_date):
    """Build a mailto: URL for a reminder (subject + body, URL-encoded)."""
    import urllib.parse
    subject = f"Reminder: {name} due {due_date.isoformat()}"
    body = f"{message}\n\nDue: {due_date.isoformat()}\n"
    params = urllib.parse.urlencode({"subject": subject, "body": body})
    return f"mailto:{TO_EMAIL or 'you@example.com'}?{params}" if TO_EMAIL else None


def render_reminder(name, due_date, message, kind, extra=""):
    """Render a single reminder as printable email-like text."""
    lines = [
        f"To: {TO_EMAIL or 'you@example.com'}",
        f"Subject: Reminder: {name} ({kind})",
        "",
        message,
        "",
        f"Due: {due_date.isoformat()}",
        f"Kind: {kind}{extra}",
    ]
    return "\n".join(lines)


def check_reminders(path, within_days=7, today=None, dry_run=True):
    """Print reminders due today/upcoming/overdue. Dry-run by default."""
    today = today or date.today()
    reminders = parse_reminders(path)
    if not reminders:
        print("No reminders found in", path)
        print(f"Add lines like: {REMINDER_LINE}")
        return 0

    due_today, upcoming, overdue = categorize(reminders, today, within_days)

    if due_today:
        print(f"DUE TODAY ({len(due_today)}):")
        for name, due_date, message, line_no in due_today:
            print(f"  - {name} — {message}")
            if dry_run:
                mt = mailto(name, message, due_date)
                if mt:
                    print(f"      mailto: {mt}")
    else:
        print("Nothing due today.")

    if upcoming:
        print(f"\nUPCOMING (within {within_days} days):")
        for name, due_date, message, days, line_no in sorted(
                upcoming, key=lambda r: r[1]):
            day_word = "tomorrow" if days == 1 else f"in {days} day(s)"
            print(f"  - {name} — due {due_date.isoformat()} — {message} ({day_word})")
    else:
        print(f"\nNo upcoming reminders within {within_days} days.")

    if overdue:
        print("\nOVERDUE:")
        for name, due_date, message, days, line_no in sorted(
                overdue, key=lambda r: r[1]):
            print(f"  - {name} — due {due_date.isoformat()} — {message} "
                  f"({days} day(s) overdue)")
    else:
        print("No overdue reminders.")

    if dry_run:
        print("\n(Dry-run: nothing was sent. Pass --apply and set SMTP_* "
              "environment variables to send for real.)")

    return 0


def send_via_smtp(name, due_date, message, kind):
    """Send one reminder email via SMTP using environment variables."""
    import smtplib
    from email.message import EmailMessage

    missing = [v for v, val in (
        ("SMTP_HOST", SMTP_HOST), ("SMTP_USER", SMTP_USER),
        ("SMTP_PASS", SMTP_PASS), ("FROM_EMAIL", FROM_EMAIL),
        ("TO_EMAIL", TO_EMAIL)) if not val]
    if missing:
        print(f"Error: cannot send, missing env vars: {', '.join(missing)}",
              file=sys.stderr)
        return 1

    msg = EmailMessage()
    msg["From"] = FROM_EMAIL
    msg["To"] = TO_EMAIL
    msg["Subject"] = f"Reminder: {name} ({kind}) — due {due_date.isoformat()}"
    msg.set_content(f"{message}\n\nDue: {due_date.isoformat()}\nKind: {kind}")

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as server:
            server.starttls()
            if SMTP_USER and SMTP_PASS:
                server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        print(f"Sent reminder for {name} to {TO_EMAIL}")
        return 0
    except Exception as exc:  # noqa: BLE001 - report send failure
        print(f"Error: failed to send reminder for {name}: {exc}", file=sys.stderr)
        return 1


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)

    within_days = 7
    dry_run = True
    path = None

    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg in ("--apply", "-a"):
            dry_run = False
        elif arg == "--dry-run" or arg == "-n":
            dry_run = True
        elif arg == "--within" and i + 1 < len(argv):
            try:
                within_days = int(argv[i + 1])
            except ValueError:
                print(f"Error: --within must be a number, got: {argv[i + 1]}",
                      file=sys.stderr)
                return 1
            i += 1
        elif not arg.startswith("-"):
            path = arg
        else:
            print(f"Error: unknown option: {arg}", file=sys.stderr)
            return 1
        i += 1

    if path is None:
        print("Usage: python3 email_reminders.py <reminders.txt> [--within N] "
              "[--apply]", file=sys.stderr)
        print(f"\nEach non-comment line looks like: {REMINDER_LINE}")
        print("Example: Electric bill | 2026-11-05 | Pay the electric bill")
        print("\n--within N   report reminders due within N days (default 7)")
        print("--apply      send via SMTP using SMTP_* env vars (default: dry-run)")
        print("\nSafety: defaults to dry-run, sends nothing. No credentials in code.")
        return 1

    if dry_run:
        return check_reminders(path, within_days=within_days, dry_run=True)

    # --apply: send each due/upcoming/overdue reminder via SMTP.
    today = date.today()
    reminders = parse_reminders(path)
    if not reminders:
        print("No reminders found in", path)
        return 0

    due_today, upcoming, overdue = categorize(reminders, today, within_days)
    to_send = due_today + upcoming + overdue
    if not to_send:
        print("No reminders due, upcoming, or overdue right now.")
        return 0

    sent = 0
    for name, due_date, message, *_ in to_send:
        kind = "overdue" if due_date < today else ("today" if due_date == today else "upcoming")
        if send_via_smtp(name, due_date, message, kind) == 0:
            sent += 1
    print(f"\nSent {sent} of {len(to_send)} reminder(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
