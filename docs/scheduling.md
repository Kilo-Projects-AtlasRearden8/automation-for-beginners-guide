# Scheduling

Want a task to run automatically on a schedule — every morning, every hour,
every Sunday? This guide shows you how to schedule tasks using built-in tools:
cron on Mac/Linux, Task Scheduler on Windows.

## What this does

`scripts/schedule_task.py` helps you add, list, and remove scheduled jobs in
your user crontab (Mac/Linux). It defaults to dry-run: it prints exactly what
it would do without changing anything. With `--apply`, it writes to your crontab
(a backup is made first).

On Windows, cron isn't available, so the guide prints the equivalent Task
Scheduler (`schtasks`) command for you to run yourself.

## Step 1: See what's already scheduled

```bash
python3 scripts/schedule_task.py --list
```

This is read-only and safe to run anytime.

## Step 2: Preview adding a job

A cron schedule has five fields: minute hour day month weekday. For example,
`*/15 * * * *` means every 15 minutes.

```bash
python3 scripts/schedule_task.py --add '*/15 * * * *' 'python3 my_backup.py'
```

This prints the cron line it would add, without changing your crontab.

## Step 3: Add the job for real

When the preview looks right, add `--apply`:

```bash
python3 scripts/schedule_task.py --add '*/15 * * * *' 'python3 my_backup.py' --apply
```

A backup of your current crontab is saved to `~/.crontab.backup` before any
change.

## Step 4: Remove a job

```bash
python3 scripts/schedule_task.py --remove 'python3 my_backup.py' --apply
```

## Windows (Task Scheduler)

Cron isn't available on Windows. Use Task Scheduler instead, e.g.:

```
schtasks /create /tn "MyBackup" /tr "python3 my_backup.py" /sc minute /mo 15
```

See `docs/scheduling.md` and the script's `--help` for details.

## The script

See `scripts/schedule_task.py`. Standard library only. It only touches your own
user crontab and never runs commands on your behalf — it just registers the
schedule.

## Safety reminder

Preview first, then add `--apply`. Only your own crontab is touched. A backup
is made before any change so you can restore it if needed.
