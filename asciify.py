import sys, re, time, argparse, signal
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BANNER = """
  ██████╗  ██████╗ ██████╗██╗██╗███████╗██╗   ██╗
  ██╔══██╗██╔════╝██╔════╝██║██║██╔════╝╚██╗ ██╔╝
  ███████║╚█████╗ ██║     ██║██║█████╗   ╚████╔╝
  ██╔══██║ ╚═══██╗██║     ██║██║██╔══╝    ╚██╔╝
  ██║  ██║██████╔╝╚██████╗██║██║██║        ██║
  ╚═╝  ╚═╝╚═════╝  ╚═════╝╚═╝╚═╝╚═╝        ╚═╝
  convert anything into ascii art
  made by @mdabdullah008
"""
# yes i vibecoded some of the functions and the banner too :P

# space = bright pixel, dense = dark pixel (black bg)
# flip with --invert if ur on a white terminal
RAMPS = {
    "detailed": " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$",
    "standard": " .:=-*+#@%",
    "blocks":   " ░▒▓█",
    "simple":   " .-:=+*%@#",
    "braille":  "⠀⠁⠂⠃⠄⠅⠆⠇⠈⠉⠊⠋⠌⠍⠎⠏⠐⠑⠒⠓⠔⠕⠖⠗⠘⠙⠚⠛⠜⠝⠞⠟⠠⠡⠢⠣⠤⠥⠦⠧⠨⠩⠪⠫⠬⠭⠮⠯⠰⠱⠲⠳⠴⠵⠶⠷⠸⠹⠺⠻⠼⠽⠾⠿⣿",
}

is_tty = sys.stdout.isatty()
strip_ansi = lambda t: re.sub(r"\033\[[^m]*m", "", t)
ansi_color = lambda r,g,b,c: f"\033[38;2;{r};{g};{b}m{c}\033[0m"
to_char = lambda v, ramp: ramp[int(v * (len(ramp)-1))]

def flatten(img, invert):
    img = img.convert("RGBA")
    bg = Image.new("RGBA", img.size, (255,255,255,255) if invert else (0,0,0,255))
    bg.paste(img, mask=img.split()[3])
    return bg.convert("RGB")

def to_ascii(img, width, ramp, colored, invert, max_h=None, raw=False, _cols=None, _rows=None):
    img = flatten(img, invert)
    w, h = img.size
    aspect = h / w

    if _cols and _rows:
        # explicit dims for video export - skip terminal 0.45 recalc
        cols, rows = _cols, _rows
    else:
        rows = max(1, int(width * aspect * 0.45))
        if max_h and rows > max_h:
            rows = max_h
            width = max(1, int(rows / aspect / 0.45))
        cols = width

    img = img.resize((cols, rows), Image.LANCZOS)
    rgb = img.convert("RGB")
    gray = img.convert("L")

    if raw:
        return [
            [(to_char(gray.getpixel((x,y))/255 if not invert else 1-gray.getpixel((x,y))/255, ramp),
              rgb.getpixel((x,y))) for x in range(cols)]
            for y in range(rows)
        ]

    out = []
    for y in range(rows):
        line = []
        for x in range(cols):
            v = gray.getpixel((x,y)) / 255
            if invert: v = 1 - v
            ch = to_char(v, ramp)
            if colored and is_tty:
                r,g,b = rgb.getpixel((x,y))
                ch = ansi_color(r,g,b,ch)
            line.append(ch)
        out.append("".join(line))
    return "\n".join(out)

def clear(): print("\033[H\033[J", end="", flush=True)
def hide_cursor(): print("\033[?25l", end="", flush=True)
def show_cursor(): print("\033[?25h", end="", flush=True)

def gif_frames(path):
    img = Image.open(path)
    frames, durations = [], []
    try:
        while True:
            frames.append(img.copy())
            durations.append(img.info.get("duration", 100) / 1000)
            img.seek(img.tell() + 1)
    except EOFError:
        pass
    return frames, durations

def play(path, width, ramp, colored, invert, loop, loops, fps, max_h=None):
    raw_frames, durations = gif_frames(path)
    frames = [to_ascii(f, width, ramp, colored, invert, max_h) for f in raw_frames]

    forever = loop or loops == 0
    n = 0
    hide_cursor()
    try:
        while True:
            for frame, dur in zip(frames, durations):
                clear()
                print(frame, flush=True)
                time.sleep(1/fps if fps else dur)
            n += 1
            if not forever and n >= loops:
                break
    finally:
        show_cursor()

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}

def ascii_to_image(text, font, bg, fg):
    lines = text.split("\n")
    cw, ch = char_size(font, 12)
    cols = max(len(l) for l in lines)
    img = Image.new("RGB", (cols*cw, len(lines)*ch), bg)
    draw = ImageDraw.Draw(img)
    for y, line in enumerate(lines):
        draw.text((0, y*ch), line, font=font, fill=fg)
    return img

def show_image(path, width, ramp, colored, invert, output, max_h=None, font_size=12, bg=(0,0,0), fg=(255,255,255)):
    img = Image.open(path)
    if output and output.suffix.lower() in IMAGE_EXTS:
        font = load_font(min(font_size, 8))
        cw, ch = char_size(font, min(font_size, 8))
        ow, oh = img.size
        cols = max(1, round(ow / cw))
        rows = max(1, round(oh / ch))
        grid = to_ascii(img, cols, ramp, colored, invert, rows, raw=True)
        vw, vh = cols * cw, rows * ch
        vw, vh = cols * cw, rows * ch
        frame = render_frame(grid, font, cw, ch, vw, vh, bg, colored if is_tty else False, fg)
        frame.save(str(output))
        print(f"saved image to {output} ({vw}x{vh})")
    else:
        result = to_ascii(img, width, ramp, colored, invert, max_h)
        if output:
            output.write_text(strip_ansi(result))
            print(f"saved to {output}")
        else:
            print(result)

def load_font(size):
    for name in ["DejaVuSansMono.ttf", "Courier New.ttf", "cour.ttf", "LiberationMono-Regular.ttf"]:
        try: return ImageFont.truetype(name, size)
        except: pass
    return ImageFont.load_default()

def char_size(font, size):
    tmp = ImageDraw.Draw(Image.new("RGB", (size*4, size*4)))
    bb = tmp.textbbox((0,0), "W", font=font)
    cw = max(1, bb[2]-bb[0])
    ascent, descent = font.getmetrics()
    ch = max(1, ascent + descent)
    return cw, ch

def render_frame(grid, font, cw, ch, vw, vh, bg, colored, fg):
    img = Image.new("RGB", (vw, vh), bg)
    draw = ImageDraw.Draw(img)
    for y, row in enumerate(grid):
        for x, (ch_char, color) in enumerate(row):
            draw.text((x*cw, y*ch), ch_char, font=font, fill=color if colored else fg)
    return img

def export(path, out, width, ramp, colored, invert, max_h, fps, loops, font_size, bg, fg):
    try:
        import cv2, numpy as np
    except:
        print("need: pip install opencv-python numpy"); sys.exit(1)

    raw_frames, durations = gif_frames(path)
    avg = sum(durations) / len(durations)
    fps = fps or (1/avg if avg > 0 else 10)

    font = load_font(font_size)
    cw, ch = char_size(font, font_size)

    ow, oh = raw_frames[0].size
    cols = max(1, round(ow / cw)) if not max_h else width
    rows = max(1, round(cols * cw * oh / (ch * ow)))
    if max_h and rows > max_h:
        rows = max_h
        cols = max(1, round(rows * ch * ow / (cw * oh)))

    vw = cols * cw; vw += vw % 2
    vh = rows * ch; vh += vh % 2

    print(f"gif {ow}x{oh} -> grid {cols}x{rows} -> video {vw}x{vh} @ {fps:.1f}fps")

    grids = []
    for i, f in enumerate(raw_frames):
        grids.append(to_ascii(f, cols, ramp, colored, invert, raw=True, _cols=cols, _rows=rows))
        print(f"  converting {i+1}/{len(raw_frames)}", end="\r")
    print()

    if loops > 1:
        grids = grids * loops

    writer = cv2.VideoWriter(str(out), cv2.VideoWriter_fourcc(*"mp4v"), fps, (vw, vh))
    for i, grid in enumerate(grids):
        frame = render_frame(grid, font, cw, ch, vw, vh, bg, colored, fg)
        writer.write(cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR))
        print(f"  writing {i+1}/{len(grids)}", end="\r")
    writer.release()
    print(f"\ndone -> {out}")


def export_gif(path, out, ramp, colored, invert, fps, loops, font_size, bg, fg):
    raw_frames, durations = gif_frames(path)
    avg = sum(durations) / len(durations)
    fps = fps or (1/avg if avg > 0 else 10)

    font = load_font(font_size)
    cw, ch = char_size(font, font_size)

    ow, oh = raw_frames[0].size
    cols = max(1, round(ow / cw))
    rows = max(1, round(oh / ch))
    vw = cols * cw
    vh = rows * ch

    print(f"gif {ow}x{oh} -> grid {cols}x{rows} -> gif {vw}x{vh} @ {fps:.1f}fps")

    pil_frames = []
    for i, f in enumerate(raw_frames):
        grid = to_ascii(f, cols, ramp, colored, invert, raw=True, _cols=cols, _rows=rows)
        pil_frames.append(render_frame(grid, font, cw, ch, vw, vh, bg, colored, fg))
        print(f"  converting {i+1}/{len(raw_frames)}", end="\r")
    print()

    dur_ms = int(1000 / fps)
    loop_count = 0 if loops == 0 else loops
    pil_frames[0].save(
        str(out),
        save_all=True,
        append_images=pil_frames[1:],
        duration=dur_ms,
        loop=loop_count,
        optimize=False,
    )
    print(f"done -> {out}")

def parse_color(s):
    try:
        p = [int(x) for x in s.split(",")]
        assert len(p) == 3
        return tuple(p)
    except:
        raise argparse.ArgumentTypeError(f"bad color '{s}', use R,G,B")

def main():
    p = argparse.ArgumentParser(description="")
    p.add_argument("file", type=Path)
    p.add_argument("-w", "--width", type=int, default=80)
    p.add_argument("-H", "--height", type=int, default=None)
    p.add_argument("-r", "--ramp", choices=RAMPS.keys(), default="standard")
    p.add_argument("-c", "--color", action="store_true")
    p.add_argument("-i", "--invert", action="store_true", help="use on white bg terminals")
    p.add_argument("-l", "--loop", action="store_true")
    p.add_argument("--loops", type=int, default=0, help="0 = forever")
    p.add_argument("-f", "--fps", type=float, default=None)
    p.add_argument("-o", "--output", type=Path, default=None, help="save output: .txt (ascii text), .png/.jpg/.webp/.bmp (image), .gif (animated gif)")
    p.add_argument("-V", "--video", type=Path, default=None, help="export as video: .mp4, .avi, .mov, .mkv")
    p.add_argument("--font-size", type=int, default=12)
    p.add_argument("--bg", default="0,0,0")
    p.add_argument("--fg", default="255,255,255")
    if len(sys.argv) == 1:
        print(BANNER)
        p.print_help()
        print("\nerror: no file given")
        sys.exit(1)
    args = p.parse_args()

    if not args.file.exists():
        print(f"file not found: {args.file}"); sys.exit(1)

    ramp = RAMPS[args.ramp]
    bg = parse_color(args.bg)
    fg = parse_color(args.fg)

    signal.signal(signal.SIGINT, lambda *_: (show_cursor(), sys.exit(0)))

    is_gif = args.file.suffix.lower() == ".gif"
    out_is_gif = args.output and args.output.suffix.lower() == ".gif"

    if args.video:
        export(args.file, args.video, args.width, ramp, args.color, args.invert,
               args.height, args.fps, args.loops, args.font_size, bg, fg)
    elif is_gif and out_is_gif:
        export_gif(args.file, args.output, ramp, args.color, args.invert,
                   args.fps, args.loops, args.font_size, bg, fg)
    elif is_gif and not args.output:
        play(args.file, args.width, ramp, args.color, args.invert,
             args.loop, args.loops, args.fps, args.height)
    else:
        show_image(args.file, args.width, ramp, args.color, args.invert, args.output, args.height,
                   args.font_size, bg, fg)

if __name__ == "__main__":
    main()
