# Startup Hub Telugu

Content for the Instagram page [@startup_hub_telugu](https://www.instagram.com/startup_hub_telugu/): startups, funding, and how companies actually make money.

Reels are in Telugu. Carousels are in simple English, with captions mixing Telugu and English.

## Folder structure

```
brand/                 Profile picture and its source
  profile.html
  profile-picture.png
posts/
  001-funding-stages/  One folder per post
    slides.html        Slide source (edit the text here)
    slide-01.png ...   Rendered slides, ready to upload
    caption.txt        Caption and hashtags
reels/
  001-funding-stages/  Telugu reel script, frames.html + frame-XX.png (9:16 backgrounds)
render.sh              Turns slides.html / frames.html into PNGs
build_reel.py          Frames + voice recording into reel.mp4
```

## Making a new post

1. Copy the last post folder, e.g. `posts/001-funding-stages` to `posts/002-how-zomato-makes-money`.
2. Edit the `slides` list in `slides.html`.
3. Render: `./render.sh posts/002-how-zomato-makes-money`
4. Write `caption.txt`.

## Making a reel

1. Render the frames: `./render.sh reels/001-funding-stages`
2. Record the script with a 1 second pause between lines. Save it in the reel folder as `voice.m4a`.
3. Build the video: `python build_reel.py reels/001-funding-stages` (needs `pip install imageio-ffmpeg`)
4. Upload `reel.mp4` on instagram.com.

## Brand

| | |
|---|---|
| Background | `#0B1020` navy |
| Accent | `#C6FF3D` lime |
| Text | `#F4F1EA` off white |
| Headings | Space Grotesk |
| Body | Inter |
| Slide size | 1080 x 1350 (4:5) |

## Style rules

- No em dashes or en dashes anywhere. Use commas or full stops.
- Check every number and fact before posting.

## Posted

| # | Post | Date |
|---|---|---|
| 001 | Startup funding stages (carousel) | 2026-09-26 |
| R001 | Startup funding stages (Telugu reel) | 2026-09-27 |
