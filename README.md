# ASCIIfy
<img width="1368" height="234" alt="ASCIIFY" src="https://github.com/user-attachments/assets/f9ab6462-3827-48c0-ba6d-f9cea777ed97" />

A command-line tool that converts images and GIFs into ASCII art — right in your terminal, or saved as a file. Supports colored output, multiple character ramps, animated GIF playback, and even video export.

---

## Requirements

- Python 3.7+
- [Pillow](https://pillow.readthedocs.io/)

```bash
pip install Pillow
```

For video export (`.mp4`, `.avi`, etc.) you'll also need:

```bash
pip install opencv-python numpy
```

---

## Basic Usage

```bash
python asciify.py <image_or_gif>
```

Drop any image in and it'll print ASCII art to your terminal.

---

## Options

| Flag | What it does |
|------|-------------|
| `-w`, `--width` | Width in characters (default: `80`) |
| `-H`, `--height` | Max height in rows (optional) |
| `-r`, `--ramp` | Character set to use (see below) |
| `-c`, `--color` | Enable full RGB color output (TTY only) |
| `-i`, `--invert` | Invert brightness — use this on white/light terminals |
| `-l`, `--loop` | Loop GIF playback forever |
| `--loops N` | Loop GIF N times (`0` = forever) |
| `-f`, `--fps` | Override playback/export frame rate |
| `-o`, `--output` | Save output to a file (`.txt`, `.png`, `.jpg`, `.gif`, etc.) |
| `-V`, `--video` | Export GIF as a video file (`.mp4`, `.avi`, `.mov`, `.mkv`) |
| `--font-size` | Font size for image/video export (default: `12`) |
| `--bg` | Background color as `R,G,B` (default: `0,0,0`) |
| `--fg` | Foreground color as `R,G,B` (default: `255,255,255`) |

---

## Character Ramps

The `-r` / `--ramp` flag controls which characters are used to represent pixel brightness.

| Ramp | Description |
|------|-------------|
| `standard` *(default)* | Simple and clean: ` .:=-*+#@%` |
| `detailed` | Long gradient for high-detail output |
| `blocks` | Unicode block chars: ` ░▒▓█` |
| `simple` | Minimal: ` .-:=+*%@#` |
| `braille` | Braille Unicode dots — great for high-res look |

---

## Examples

**Print image as ASCII art:**
```bash
python asciify.py photo.jpg
```

**Colored ASCII art, wider output:**
```bash
python asciify.py photo.png -c -w 120
```

**Invert for a white/light terminal:**
```bash
python asciify.py photo.jpg -i
```

**Use the detailed ramp:**
```bash
python asciify.py photo.png -r detailed -w 100
```

**Save as a text file:**
```bash
python asciify.py photo.jpg -o output.txt
```

**Save as an ASCII art image (PNG):**
```bash
python asciify.py photo.jpg -o output.png
```

**Play an animated GIF in the terminal:**
```bash
python asciify.py animation.gif
```

**Loop a GIF forever:**
```bash
python asciify.py animation.gif --loop
```

**Export a GIF as an ASCII art video:**
```bash
python asciify.py animation.gif -V output.mp4
```

**Export a GIF as an ASCII art GIF:**
```bash
python asciify.py animation.gif -o output.gif
```

**Custom colors for export (white bg, black text):**
```bash
python asciify.py photo.jpg -o output.png --bg 255,255,255 --fg 0,0,0
```

---

## Notes

- Color output (`-c`) only works in a real terminal (TTY). It's silently ignored when piping output or saving to a file.
- For best results, use `--invert` if your terminal has a light/white background.
- The `--font-size` option only affects image and video export — it has no effect on terminal output.
- Transparent images are composited onto a black (or white, if `--invert`) background before conversion.

---
