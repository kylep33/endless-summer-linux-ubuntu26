#!/usr/bin/env python3
"""Cut the transition clips in ../transitions/ from two YouTube sources.

Provenance (personal use only, not redistributable):
  jAqkiw0bsg4  "Surf's Up but only Chicken Joe scenes" (Sony Pictures Animation, 2007)
  hg4FvOi-N18  The Sandals - "Theme from The Endless Summer" (1964)

Needs: yt-dlp, faster-whisper, numpy, imageio-ffmpeg (pip, in a venv).
  yt-dlp -x --audio-format wav -o '%(id)s.%(ext)s' <url>   # into SRC
  python make-clips.py SRC_DIR
Joe lines are located by whisper word timestamps, so cuts land on the words.
"""
import json, os, re, subprocess, sys
import imageio_ffmpeg

SRC = sys.argv[1]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "transitions")
FF = imageio_ffmpeg.get_ffmpeg_exe()
JOE, THEME = "jAqkiw0bsg4", "hg4FvOi-N18"

# pool -> list of (name, phrase) for Joe, or (name, start, end) seconds for the theme
CLIPS = {
    "login_sounds": [
        ("theme-a", 8.5, 16.6), ("theme-b", 16.5, 24.6), ("theme-c", 28.5, 36.6), ("theme-d", 40.5, 48.6),
        ("im-chicken-joe", "always pays off. I'm Chicken Joe, man"),
        ("im-flying", "Whoo-hoo! I'm flying"),
        ("joseph", "Chicken Joe. Joseph, it's long for Joe", -0.2),  # stop before the penguins chant
        ("brain-freeze", "You gotta try this blowhole thing, man. This whale dude is giving me a brain freeze"),
        ("dinner-and-a-show", "It was like dinner and a show"),
    ],
    "logout_sounds": [
        ("theme-intro", 0.4, 8.5),
        ("see-you-in-the-lineup", "I'll see you in the lineup"),
        ("see-you-guys-later", "See you guys later"),
        ("vision-of-my-quest", "As enjoyable as it was, I still had a vision of my quest"),
        ("peaceful-jungle", "the jungle's the most peaceful place on the planet"),
        ("lake-michigan", "Dude, I'm from Lake Michigan"),
    ],
    "notification_sounds": [
        ("sweet-man", "Sweet, man", 0.3),  # whisper squashed this one
        ("check-it-out", "Check it out"),
        ("thats-cool", "That's cool"),
        ("got-it", "Got it"),
        ("you-gotta-try-this", "Dude, you gotta try this"),
        ("opened-my-pores", "It really opened up my pores, you know"),
        ("feel-it-in-my-nuggets", "I can feel him in my nuggets"),
    ],
    "error_sounds": [
        ("lost-a-bet", "I lost a bet"),
        ("oh-crap", "Oh, crap"),
        ("i-won", "I won"),
        ("sight-of-blood", "I can't stand the sight of blood"),
        ("heavier", "You are heavier than you look"),
        ("yum", "Yum, yum, yum, yum, yum, yum"),
    ],
}

norm = lambda s: re.sub(r"[^a-z0-9 ]", "", re.sub(r"-", " ", s.lower())).split()
words = json.load(open(os.path.join(SRC, JOE + ".wav.words.json")))
# whisper may split or join words differently from the phrase, so match on a flat token stream
toks, owner = [], []
for i, (w, _, _) in enumerate(words):
    for t in norm(w):
        toks.append(t)
        owner.append(i)


def find(phrase):
    p = norm(phrase)
    for i in range(len(toks) - len(p) + 1):
        if toks[i:i + len(p)] == p:
            return words[owner[i]][1] - 0.12, words[owner[i + len(p) - 1]][2] + 0.4  # whisper ends words early
    sys.exit(f"phrase not found: {phrase!r}")


def cut(src, start, end, out):
    d = end - start
    subprocess.run([FF, "-v", "error", "-y", "-ss", f"{start:.3f}", "-t", f"{d:.3f}", "-i", src,
                    "-af", f"afade=in:d=0.005,afade=out:st={d - 0.2:.3f}:d=0.2,loudnorm=I=-18:TP=-1.5",  # quick 200 ms tail-off
                    "-ar", "48000", "-ac", "2", "-sample_fmt", "s16", out], check=True)


for pool, clips in CLIPS.items():
    os.makedirs(os.path.join(OUT, pool), exist_ok=True)
    for name, *spec in clips:
        if isinstance(spec[0], str):  # Joe line, optional extra tail in seconds
            src, (a, b) = JOE, find(spec[0])
            b += spec[1] if len(spec) > 1 else 0
        else:
            src, (a, b) = THEME, spec
        cut(os.path.join(SRC, src + ".wav"), a, b, os.path.join(OUT, pool, name + ".wav"))
        print(f"{pool}/{name}: {b - a:.1f}s")
