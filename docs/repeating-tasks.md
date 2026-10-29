# Repeating Tasks

Want to run the same command over and over — a backup, a check, a quick test —
on a timer? This guide shows you how to repeat a command every N seconds,
safely.

## What this does

`scripts/repeat_task.py` runs a command you give it, every N seconds, up to M
times (or forever if you don't set a limit). It defaults to dry-run: it prints
the schedule without running anything, so you can see exactly what will happen
before anything runs.

## Step 1: Preview the schedule

```bash
python3 scripts/repeat_task.py "echo hello" --every 10 --times 3
```

This prints what it would run, every 10 seconds, 3 times — without executing
anything.

## Step 2: Run for real

When the preview looks right, add `--apply`:

```bash
python3 scripts/repeat_task.py "echo hello" --every 10 --times 3 --apply
```

The command runs immediately, then again every 10 seconds, 3 times total. Press
Ctrl-C to stop early.

## Options

- `--every N` — seconds between runs (default 60)
- `--times M` — stop after M runs (default: repeat forever)
- `--apply` — run the command for real (default is preview only)

## Examples

Repeat a backup script every hour, 4 times:

```bash
python3 scripts/repeat_task.py "python3 my_backup.py" --every 3600 --times 4 --apply
```

Say "hello" every 5 seconds forever (preview only):

```bash
python3 scripts/repeat_task.py "echo hello" --every 5
```

## The script

See `scripts/repeat_task.py`. Standard library only, about 100 lines, no
secrets or credentials.

## Safety reminder

Preview first with `--every` and `--times` but *without* `--apply`. Only add
`--apply` once you're sure the command and timing are what you want. Each run
has a 60-second timeout so one stuck command can't hang forever.
