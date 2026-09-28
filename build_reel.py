"""Build a 9:16 reel video from frame-XX.png images and a voice recording.

Usage: python build_reel.py reels/001-funding-stages

Put your recording in the reel folder as voice.m4a / .mp3 / .wav / .webm / .ogg.
Read the script with a clear pause (about 1 second) between lines: the frame
changes at each pause. Without a voice file, a silent preview is made instead
(5 seconds per frame).
Output: <reel folder>/reel.mp4
"""
import re
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
PREVIEW_SECONDS = 5.0


def run(args):
    return subprocess.run([FFMPEG, "-hide_banner", *args], capture_output=True, text=True)


def audio_length(voice):
    out = run(["-i", str(voice)]).stderr
    h, m, s = re.search(r"Duration: (\d+):(\d+):([\d.]+)", out).groups()
    return int(h) * 3600 + int(m) * 60 + float(s)


def pauses(voice):
    """Return (start, end) of each quiet stretch in the recording."""
    out = run(["-i", str(voice), "-af", "silencedetect=noise=-35dB:d=0.5", "-f", "null", "-"]).stderr
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", out)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", out)]
    return list(zip(starts, ends))


def frame_durations(voice, count):
    total = audio_length(voice)
    quiet = pauses(voice)
    # Ignore silence at the very start and end; those aren't between lines.
    inner = [(s, e) for s, e in quiet if s > 0.3 and e < total - 0.3]
    if len(inner) < count - 1:
        print(f"Found only {len(inner)} pauses for {count} frames; splitting evenly instead.")
        return [total / count] * count
    # The longest pauses are the ones between lines.
    cuts = sorted(sorted(inner, key=lambda p: p[1] - p[0], reverse=True)[: count - 1])
    marks = [0.0] + [(s + e) / 2 for s, e in cuts] + [total]
    return [b - a for a, b in zip(marks, marks[1:])]


def main():
    folder = Path(sys.argv[1]).resolve()
    frames = sorted(folder.glob("frame-*.png"))
    if not frames:
        sys.exit(f"No frame-XX.png files in {folder}. Run ./render.sh first.")
    voice = next((p for ext in ("m4a", "mp3", "wav", "webm", "ogg", "aac")
                  for p in folder.glob(f"voice.{ext}")), None)

    durations = frame_durations(voice, len(frames)) if voice else [PREVIEW_SECONDS] * len(frames)
    for f, d in zip(frames, durations):
        print(f"{f.name}: {d:.1f}s")

    playlist = folder / "frames.txt"
    lines = [f"file '{f.name}'\nduration {d:.3f}" for f, d in zip(frames, durations)]
    playlist.write_text("\n".join(lines) + f"\nfile '{frames[-1].name}'\n", encoding="utf-8")

    out = folder / "reel.mp4"
    args = ["-y", "-f", "concat", "-safe", "0", "-i", str(playlist)]
    if voice:
        args += ["-i", str(voice), "-c:a", "aac", "-b:a", "192k", "-shortest"]
    args += ["-vf", "fps=30,scale=1080:1920,format=yuv420p", "-c:v", "libx264",
             "-preset", "medium", "-crf", "18", "-movflags", "+faststart", str(out)]
    result = run(args)
    playlist.unlink()
    if result.returncode != 0:
        sys.exit(result.stderr[-2000:])
    print(f"Done: {out} ({sum(durations):.1f}s{'' if voice else ', silent preview'})")


if __name__ == "__main__":
    main()
