# STATUS — Simple Automation for Beginners

## What was built

A beginner-friendly manual on safe, everyday automation, published by **Asdale
Dynamics, LLC** (credit to Dylan Asdale, registered nurse turned AI author and
founder of Asdale Dynamics, LLC). Covers four topics using built-in tools and
tiny, auditable Python scripts: organizing files, repeating tasks, email
reminders, and scheduling.

**Project contents**

- `README.md` — overview, how to use, credits Asdale Dynamics, LLC.
- `LICENSE` — MIT License, copyright line exactly
  `Copyright (c) 2026 Asdale Dynamics, LLC`.
- `docs/` — beginner manual in Markdown:
  - `overview.md` — welcome and table of contents
  - `safety.md` — safety first (test on copies, never move originals)
  - `file-organization.md` — sort a folder into type-based subfolders
  - `repeating-tasks.md` — repeat a command on a timer
  - `email-reminders.md` — reminders from a local `reminders.txt`
  - `scheduling.md` — cron / Task Scheduler scheduling
- `scripts/` — tiny, auditable Python scripts (standard library only; no
  `pip install`, no API keys, no secrets):
  - `organize_files.py`
  - `repeat_task.py`
  - `email_reminders.py`
  - `schedule_task.py`
- `tests/` — test suite for each script:
  - `test_organize_files.py`
  - `test_repeat_task.py`
  - `test_email_reminders.py`
  - `test_schedule_task.py`
- `static/` — fully static HTML site mirroring the docs (no build step, no
  server needed):
  - `index.html`, `safety.html`, `file-organization.html`,
    `repeating-tasks.html`, `email-reminders.html`, `scheduling.html`,
    `checklist.html`, `style.css`
- `static/checklist.html` — printable checklist/worksheet with checkboxes
- `.gitignore` — excludes `__pycache__`, `.env`, `.venv`, and personal data
  files (`reminders.txt`, `bills.txt`)
- `STATUS.md` — this file

## How to run it

### Read the manual
- Markdown: open any file in `docs/`.
- HTML: open `static/index.html` in a browser. The site is fully static — no
  build step, no server needed.

### Run the scripts
Each script is plain Python 3, standard library only.

```
python3 scripts/organize_files.py <folder> [--apply]
python3 scripts/repeat_task.py "<command>" --every N [--times M] [--apply]
python3 scripts/email_reminders.py <reminders.txt> [--within N] [--apply]
python3 scripts/schedule_task.py --list
python3 scripts/schedule_task.py --add "<schedule>" "<command>" [--apply]
```

**Safety:** every script defaults to a non-destructive preview (dry-run) and
works on the folder/file you explicitly point at. Always test on a copy first.
See `docs/safety.md`. `email_reminders.py --apply` only sends when SMTP
environment variables are set; nothing is hardcoded.

### Run the tests
```
python3 tests/test_organize_files.py
python3 tests/test_repeat_task.py
python3 tests/test_email_reminders.py
python3 tests/test_schedule_task.py
```

### Print the checklist
Open `static/checklist.html` and print from your browser (Letter size). It's
designed to be printed and ticked off by hand.

## Verification results

All checks pass:

- `tests/test_organize_files.py` — PASS (extension grouping, copy-only
  behavior, dry-run moves nothing, duplicate avoidance, destination-folder
  skipping)
- `tests/test_repeat_task.py` — PASS (dry-run runs nothing, --apply executes
  once, argument parsing)
- `tests/test_email_reminders.py` — PASS (parsing, malformed lines and bad
  dates skipped, today/upcoming/overdue categorization, dry-run sends nothing)
- `tests/test_schedule_task.py` — PASS (cron line generation/parsing, add
  without duplicates, remove, read crontab — no system crontab touched)

All Python files compile cleanly (`py_compile`). No build step, no
dependencies beyond Python 3. No `.github/workflows` files (by design). No
secrets, API keys, or personal data in any committed file.

The repo was initialized and committed locally as one plain commit
(`943e8e7`) using the existing git identity; nothing was pushed and no remote
was created.

## Known gaps

- `email_reminders.py` SMTP sending requires the user to set `SMTP_*`
  environment variables in their own shell; it was not exercised end-to-end
  against a real mail server (no credentials available, by design).
- `schedule_task.py --apply` writes to the user's crontab only when `crontab`
  is available (Mac/Linux); on Windows the docs point to Task Scheduler
  (`schtasks`). `--apply` was not exercised against a live crontab to avoid
  modifying the user's system; pure functions are tested.
- `repeat_task.py` runs each command with a 60-second timeout; long-running
  commands are killed.
- The HTML site is hand-written (not generated from Markdown), so `docs/` and
  `static/` must be kept in sync manually.
- Bill reminders / reminders files are organizational tools, not financial or
  medical advice (noted in the docs).
