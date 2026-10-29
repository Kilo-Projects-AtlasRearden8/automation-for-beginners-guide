#!/usr/bin/env python3
"""Organize files in a folder into type-based subfolders.

Safety first: defaults to dry-run (preview only, nothing moved). Pass --apply
to actually move files. Works on the folder you point it at — always test on a
copy first. Never deletes files; only moves them into type folders.
Standard library only.
"""

import os
import shutil
import sys

EXTENSION_GROUPS = {
    ".pdf": "Documents",
    ".doc": "Documents",
    ".docx": "Documents",
    ".txt": "Documents",
    ".rtf": "Documents",
    ".odt": "Documents",
    ".xls": "Documents",
    ".xlsx": "Documents",
    ".csv": "Documents",
    ".ppt": "Documents",
    ".pptx": "Documents",
    ".jpg": "Images",
    ".jpeg": "Images",
    ".png": "Images",
    ".gif": "Images",
    ".webp": "Images",
    ".bmp": "Images",
    ".svg": "Images",
    ".mp3": "Audio",
    ".wav": "Audio",
    ".m4a": "Audio",
    ".ogg": "Audio",
    ".flac": "Audio",
    ".mp4": "Video",
    ".mov": "Video",
    ".avi": "Video",
    ".mkv": "Video",
    ".wmv": "Video",
    ".zip": "Archives",
    ".rar": "Archives",
    ".7z": "Archives",
    ".tar": "Archives",
    ".gz": "Archives",
    ".bz2": "Archives",
    ".exe": "Installers",
    ".dmg": "Installers",
    ".pkg": "Installers",
    ".msi": "Installers",
}

DEFAULT_OTHER = "Other"


def group_for_extension(ext):
    """Return the destination folder name for a file extension."""
    return EXTENSION_GROUPS.get(ext, DEFAULT_OTHER)


def organize_folder(folder, dry_run=True):
    """Sort files directly inside `folder` into type subfolders.

    Does not recurse into subfolders. Skips folders that already exist in the
    top level so we don't try to sort our own output folders.
    """
    folder = os.path.abspath(folder)
    if not os.path.isdir(folder):
        print(f"Error: not a directory: {folder}", file=sys.stderr)
        return 1

    destination_names = set(EXTENSION_GROUPS.values()) | {DEFAULT_OTHER}

    moved = 0
    skipped = 0
    for entry in os.listdir(folder):
        entry_path = os.path.join(folder, entry)

        if os.path.isdir(entry_path):
            skipped += 1
            continue

        _, ext = os.path.splitext(entry)
        if not ext:
            skipped += 1
            continue

        dest_folder = group_for_extension(ext.lower())
        dest_path = os.path.join(folder, dest_folder, entry)

        if os.path.exists(dest_path):
            base, extension = os.path.splitext(entry)
            counter = 1
            while os.path.exists(dest_path):
                dest_path = os.path.join(
                    folder, dest_folder, f"{base}-{counter}{extension}"
                )
                counter += 1

        if dry_run:
            print(f"[dry-run] would move: {entry} -> {dest_folder}/")
        else:
            os.makedirs(os.path.join(folder, dest_folder), exist_ok=True)
            shutil.move(entry_path, dest_path)
            print(f"moved: {entry} -> {dest_folder}/")
        moved += 1

    print(f"\nDone. {moved} file(s) {'would be ' if dry_run else ''}moved, "
          f"{skipped} item(s) skipped (folders or extensionless files).")
    if dry_run:
        print("Pass --apply to move for real.")
    return 0


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)

    dry_run = True
    if "--apply" in argv or "-a" in argv:
        dry_run = False
        argv.remove("--apply") if "--apply" in argv else None
        argv.remove("-a") if "-a" in argv else None

    if not argv:
        print("Usage: python3 organize_files.py <folder> [--apply]", file=sys.stderr)
        print("\nMoves files in <folder> into type-based subfolders "
              "(Documents, Images, Audio, Video, Archives, Installers, Other).")
        print("Defaults to dry-run: nothing is moved unless you pass --apply.")
        print("\nSafety: test on a copy of your folder first.")
        return 1

    return organize_folder(argv[0], dry_run=dry_run)


if __name__ == "__main__":
    sys.exit(main())
