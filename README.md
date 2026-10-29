# Simple Automation for Beginners

A beginner-friendly manual on safe, everyday automation: organizing files,
repeating tasks, email reminders, and scheduling — using only built-in tools
and tiny scripts you can read end to end. Test on copies, never move originals.

**Credit:** This manual is published by **Asdale Dynamics, LLC** (Indiana,
formed October 2026), founded by Dylan Asdale — a registered nurse turned AI
author and founder of Asdale Dynamics, LLC. Dylan writes and teaches AI "like a
friend would": plain English, step by step, never condescending. Learn more at
dylanasdale.github.io.

---

## What's inside

- `docs/` — beginner manuals in Markdown (read them here, or in the static HTML
  site under `static/`).
- `scripts/` — tiny, auditable Python scripts (standard library only). Each one
  defaults to a non-destructive preview and works on copies by default; none
  touches your originals unless you explicitly ask.
- `static/` — a fully static HTML site mirroring the docs, no build step, no
  server needed.
- `static/checklist.html` — a printable checklist/worksheet you can print and
  tick off by hand.
- `tests/` — small tests that prove the scripts behave safely.

## How to use this manual

1. **Read the safety page first** (`docs/safety.md`). The golden rule: test on
   copies, never move originals.
2. Pick a task (organizing files, repeating tasks, email reminders, scheduling)
   and read its guide in `docs/`.
3. Run the matching script in `scripts/` against a copy of your files first.
4. When you're confident, run it on your real files — or keep using copies
   forever. Either way is fine.

## License

MIT License. Copyright (c) 2026 Asdale Dynamics, LLC. See `LICENSE` for the
full text.
