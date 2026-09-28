"""Build a 9:16 reel video from frame-XX.png images and a voice recording.

Usage: python build_reel.py reels/001-funding-stages

Put your recording in the reel folder as voice.m4a / .mp3 / .wav / .webm / .ogg.
Pause briefly between lines. The frame changes at the pause nearest to where
each line should end (estimated from the line lengths in script.md). To set the
times by hand, put one cut time in seconds per line break in cuts.txt. Without a voice file, a silent preview is made instead
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
    out = run(["-i", str(voice), "-af", "silencedetect=noise=-30dB:d=0.35", "-f", "null", "-"]).stderr
    starts = [max(0.0, float(x)) for x in re.findall(r"silence_start: (-?[\d.]+)", out)]
    ends = [float(x) for x in re.findall(r"silence_end: (-?[\d.]+)", out)]
    return list(zip(starts, ends))


def line_weights(folder, count):
    """Relative length of each spoken line, from the Romanized section of script.md."""
    script = folder / "script.md"
    if script.exists():
        text = script.read_text(encoding="utf-8")
        section = text.split("## Romanized", 1)[-1].split("\n## ", 1)[0]
        lines = re.findall(r"^\d+\. (.+)$", section, re.M)
        if len(lines) == count:
            return [len(line) for line in lines]
    return [1] * count


def frame_durations(voice, folder, count):
    total = audio_length(voice)
    manual = folder / "cuts.txt"
    if manual.exists():
        # One cut time in seconds per line, overriding the automatic detection.
        cuts = [float(x) for x in manual.read_text().split()]
        print(f"Using {len(cuts)} cut times from cuts.txt")
    else:
        cuts = auto_cuts(voice, total, line_weights(folder, count), count)
    marks = [0.0] + cuts + [total]
    return [b - a for a, b in zip(marks, marks[1:])]


def auto_cuts(voice, total, weights, count):
    quiet = pauses(voice)
    speech_start = quiet[0][1] if quiet and quiet[0][0] < 0.3 else 0.0
    speech_end = quiet[-1][0] if quiet and quiet[-1][1] > total - 0.3 else total
    # Pauses between the first and last word are candidate cut points.
    cands = [(s + e) / 2 for s, e in quiet if s > speech_start and e < speech_end]
    need = count - 1
    span = speech_end - speech_start
    acc, expected = 0, []
    for w in weights[:-1]:
        acc += w
        expected.append(speech_start + span * acc / sum(weights))
    if len(cands) < need:
        print(f"Found only {len(cands)} pauses for {count} frames; using estimated times.")
        return expected
    # Pick the increasing set of pauses closest to where each line should end.
    INF = float("inf")
    best = [[INF] * len(cands) for _ in range(need)]
    prev = [[-1] * len(cands) for _ in range(need)]
    for j, c in enumerate(cands):
        best[0][j] = (c - expected[0]) ** 2
    for k in range(1, need):
        for j, c in enumerate(cands):
            for i in range(j):
                cost = best[k - 1][i] + (c - expected[k]) ** 2
                if cost < best[k][j]:
                    best[k][j], prev[k][j] = cost, i
    j = min(range(len(cands)), key=lambda x: best[need - 1][x])
    picked = []
    for k in range(need - 1, -1, -1):
        picked.append(cands[j])
        j = prev[k][j]
    return picked[::-1]


def main():
    folder = Path(sys.argv[1]).resolve()
    frames = sorted(folder.glob("frame-*.png"))
    if not frames:
        sys.exit(f"No frame-XX.png files in {folder}. Run ./render.sh first.")
    voice = next((p for ext in ("m4a", "mp3", "wav", "webm", "ogg", "aac")
                  for p in folder.glob(f"voice.{ext}")), None)

    durations = frame_durations(voice, folder, len(frames)) if voice else [PREVIEW_SECONDS] * len(frames)
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
