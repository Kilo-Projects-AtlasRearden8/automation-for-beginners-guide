# Email Reminders

Never forget a due date again. This guide shows you how to keep a simple list
of reminders in a plain text file and get reminded when something is coming up
— all on your own computer, no apps or accounts needed.

## What this does

`scripts/email_reminders.py` reads a `reminders.txt` file you maintain and tells
you which reminders are due today, coming up soon, or already overdue. In
dry-run mode (the default) it prints each reminder and a `mailto:` link you can
click to compose the email. With `--apply` and SMTP environment variables set
in your shell, it can send the email for real.

A sample `reminders.txt` looks like this:

```
# Reminder name | due date (YYYY-MM-DD) | message
Electric bill | 2026-11-05 | Pay the electric bill
Library books | 2026-11-10 | Return library books
Dentist | 2026-11-01 | Dentist appointment
```

Lines starting with `#` are comments and ignored. The date format is
year-month-day (2026-11-05).

## Step 1: Create your reminders file

Create `reminders.txt` somewhere easy to find, like your Documents folder:

```
# My reminders
Electric bill | 2026-11-05 | Pay the electric bill
Library books | 2026-11-10 | Return library books
```

Use real dates. The date format is year-month-day (2026-11-05).

## Step 2: Run the reminder (dry run)

```bash
python3 scripts/email_reminders.py ~/Documents/reminders.txt
```

You'll see what's due today, upcoming within 7 days, and overdue — plus a
`mailto:` link for each one you can click to send the email yourself.

## Step 3: Send for real (optional)

To actually send email, set these environment variables in your shell (never in
this project), then run with `--apply`:

```
export SMTP_HOST=smtp.example.com
export SMTP_USER=you@example.com
export SMTP_PASS=your-app-password
export FROM_EMAIL=you@example.com
export TO_EMAIL=you@example.com

python3 scripts/email_reminders.py ~/Documents/reminders.txt --apply
```

No credentials are stored in this script or the repo. `--apply` sends nothing
unless all SMTP variables are set.

## The script

See `scripts/email_reminders.py`. Standard library only. It never stores
passwords, API keys, or personal data.

## Notes

- This is an organizational tool, not financial or medical advice.
- All reminder data stays in `reminders.txt` on your computer.
- Do not commit `reminders.txt` — it contains your personal data. It's already
  ignored by `.gitignore`.
