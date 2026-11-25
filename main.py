"""One Star, Written in Sap -- make.fun entry (program/v1).

Design description
------------------
The bounty asks for one line of plain text, under 280 characters, in the
voice of a houseplant leaving a one-star review of its human owner. The
line has to work as a real review -- a grievance plus a reason for the
single star -- and it has to be funny. A comedy-editor judge compares
entries two at a time and keeps the funnier one, weighing in this order:

  1. a one-line 1-star review written by a houseplant about its human
     owner, with the plant's own grievance at the centre;
  2. funnier: a real laugh through a surprising turn, a sharp plant's-eye
     grievance, or a well-built joke rather than a cute idea alone;
  3. sounds like a houseplant wrote it, with a plant's view of water,
     light, soil, pots, repotting or being moved, not a person in a
     costume;
  4. reads as a genuine one-star review, with a clear complaint and a
     reason for the single star, in one line under 280 characters;
  5. fresh, specific detail and precise wording, with no stock phrases
     about drama queens, dramatic wilting or being ignored.

This program runs the same tournament locally: every candidate line is
scored on those five criteria, the best line wins, and the winner is
written to ``$MAKEFUN_OUTPUT_DIR/entry.txt`` (the grader mounts that
directory at ``/output``). The selection is fully deterministic -- the
same candidates and the same weights always pick the same line -- and
the output is validated against the sealed gate (UTF-8 text, 1 to 279
characters, not only white space, a single line, no hashtags).

Why the winner wins
-------------------
"One star. He repotted me 'for my own good' into a pot with no drainage
-- I've been standing in my own bathwater since March." opens with the
words of a posted review ("One star."), then turns a caring act into the
complaint itself: repotted "for my own good" into a pot that cannot drain.
The plant's-eye detail is concrete (repotting, no drainage, standing in
bathwater) and dated (since March), so the neglect has a duration, and
the punchline is the image of a plant standing in its own bathwater --
a grievance only a houseplant could file.
"""

import os
import re
import sys

# Candidate lines, written for this bounty. Each is one line of plain
# text, under 280 characters, in the voice of a houseplant reviewing its
# human owner. No line reuses a phrase from any other entry.
CANDIDATES = [
    "One star. He repotted me 'for my own good' into a pot with no "
    "drainage -- I've been standing in my own bathwater since March.",
    "One star. She bought me to clean the air, then chainsmokes beside "
    "me and blames my brown tips on bad vibes.",
    "One star. He talks to me every morning, which would be sweet if "
    "talking were water -- I've heard his whole divorce and I'm still "
    "thirsty.",
    "One star. She moved me to the bathroom for the humidity, so now I "
    "live above a toilet, photosynthesizing steam and shame.",
    "One star. He bought me because I was 'low maintenance', then acted "
    "surprised when low maintenance still meant water.",
    "One star. He waters me with ice cubes. I'm from the rainforest. "
    "This is not care, it's a hostage situation with extra steps.",
    "One star. I was a housewarming gift. Three moves, two years, one "
    "watering can -- and he still introduces me as 'the one that won't "
    "die'.",
    "One star. My owner googled 'why is my plant sad' and bought a "
    "second plant instead of watering the first one.",
    "One star. She misted me once, posted it, and called it self-care. "
    "I'm still thirsty and now I'm content.",
    "One star. He fertilizes me once a year, on my birthday, which he "
    "also forgets. I'm not a houseplant, I'm a calendar reminder he "
    "snoozes.",
    "One star. The care tag says bright indirect light. He heard 'dark "
    "corner behind the fridge' and now I pay rent in shadows.",
    "One star. She pruned me for 'growth' and left me shaped like a bad "
    "haircut -- I photosynthesize now out of spite and spite alone.",
]

# Plant's-eye nouns: water, light, soil, pots, repotting, being moved
# (judge criterion 3). Substring matches, so "bathwater" also counts
# as water and "repotted" as repotting.
PLANT_WORDS = (
    "repott", "drain", "water", "light", "soil", "pot", "bathwater",
    "root", "leaf", "leaves", "mist", "fertiliz", "prun", "photosynth",
    "thirst", "brown tip", "rainforest", "ice cube", "humidity",
    "steam", "toilet", "bathroom", "air", "fridge", "shadows",
)

# Surprising turns and specific detail (judge criteria 2 and 5): the
# caring act that backfires, the blame shifted onto the plant, a dated
# or counted grievance. Whole-word matches, so "still" inside another
# word does not count.
TURN_MARKERS = (
    "for my own good", "blames", "bad vibes", "still", "since",
    "march", "hostage", "extra steps", "low maintenance", "self-care",
    "divorce", "second plant", "won't die", "out of spite",
    "calendar reminder", "pay rent", "for the humidity",
)

MAX_CHARS = 279


def score(line):
    """Score one candidate on the judge's five criteria, most important
    first. Weights follow the brief's order: the review frame and the
    plant's voice matter most, then the surprising turn, then fresh
    detail. Shortness is a small tie-breaker only, so a thin line never
    beats a rich one on length alone."""
    text = line.lower()
    points = 0.0
    # 1. Reads as a posted one-star review: the line opens with the
    #    review's own words.
    if line.startswith("One star"):
        points += 2.0
    # 3. Sounds like a houseplant wrote it: count distinct plant's-eye
    #    details (water, light, soil, pots, repotting, being moved),
    #    capped at four.
    details = sum(1 for word in PLANT_WORDS if word in text)
    points += min(details, 4)
    # 2 + 5. A surprising turn with fresh, specific detail: count
    #    distinct turn markers, capped at three.
    turns = sum(1 for token in TURN_MARKERS
                if re.search(r"(?<!\w)" + re.escape(token) + r"(?!\w)",
                             text))
    points += min(turns, 3)
    # 4. Short and quotable: a gentle bonus for staying well inside the
    #    280-character limit.
    points += (MAX_CHARS - len(line)) * 0.005
    return points


def validate(line):
    """Enforce the sealed gate plus the brief's plain-text rules. Raises
    ValueError on any violation so a bad line can never be submitted."""
    if not line or not line.strip():
        raise ValueError("entry is empty or only white space")
    if "\n" in line or "\r" in line:
        raise ValueError("entry must be a single line")
    if len(line) > MAX_CHARS:
        raise ValueError("entry is %d chars, over the 279-char gate"
                         % len(line))
    if "#" in line:
        raise ValueError("entry must not contain hashtags")
    for banned in ("drama queen", "dramatic wilt", "ignored"):
        if banned in line.lower():
            raise ValueError("entry uses a banned stock phrase: %s"
                             % banned)
    return line


def pick_winner(candidates):
    """Run the local tournament: score every candidate, keep the best.
    Ties break toward the earlier candidate, so the result is stable."""
    best_line = None
    best_score = None
    for line in candidates:
        validate(line)
        points = score(line)
        if best_score is None or points > best_score:
            best_line, best_score = line, points
    return best_line, best_score


def main():
    line, points = pick_winner(CANDIDATES)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.txt")
    with open(path, "w", encoding="utf-8", newline="") as handle:
        handle.write(line)
    # Read the file back and confirm it is byte-for-byte the line the
    # tournament picked: the grader reads this file, so a short write or
    # an encoding surprise must fail here, never silently upstream.
    with open(path, "r", encoding="utf-8", newline="") as handle:
        written = handle.read()
    if written != line:
        raise ValueError("entry.txt does not match the winning line")
    print("winner (%d chars, score %.2f):" % (len(line), points))
    print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
