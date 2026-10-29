# Organizing Files

Got a messy folder — maybe Downloads — full of PDFs, images, installers, and
who knows what else? This guide shows you how to sort them into neat folders by
file type, safely, one step at a time.

## What this does

`scripts/organize_files.py` looks at every file in a folder and moves it into a
subfolder named after its type:

- `Documents/` — .pdf, .doc, .docx, .txt, .csv, .xlsx, .pptx, .rtf, .odt
- `Images/` — .jpg, .jpeg, .png, .gif, .webp, .bmp, .svg
- `Audio/` — .mp3, .wav, .m4a, .ogg, .flac
- `Video/` — .mp4, .mov, .avi, .mkv, .wmv
- `Archives/` — .zip, .rar, .7z, .tar, .gz, .bz2
- `Installers/` — .exe, .dmg, .pkg, .msi
- `Other/` — anything that doesn't match the above

Files without extensions (and folders already in the folder) are left alone.
If a file with the same name already exists in the destination, the script
renames it (`file-1.pdf`, `file-2.pdf`) instead of overwriting.

## Step 1: Make a test copy

Copy the folder you want to organize:

```bash
cp -r ~/Downloads ~/Downloads-Test
```

## Step 2: Preview first (dry run)

```bash
python3 scripts/organize_files.py ~/Downloads-Test
```

This prints what it *would* move without touching anything. Review the list
carefully.

## Step 3: Organize for real

When the preview looks right, add `--apply`:

```bash
python3 scripts/organize_files.py ~/Downloads-Test --apply
```

## Step 4: Check the results

Open the folder and confirm the files landed in the right folders. If something
is wrong, delete the test folder and try again. Only run it on your real
`~/Downloads` once you're confident.

## The script

See `scripts/organize_files.py`. It's short and every line is explained. Want a
folder for spreadsheets? Add `.xlsx` to the `Documents` group. It's your script
— edit it.

## Safety reminder

This script moves files in place (on the folder you point it at). That's why we
always test on a copy first. Your originals stay untouched until you're sure.
