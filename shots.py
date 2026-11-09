#!/usr/bin/env python3
"""Writes assets/img/<lang>/<app>-s01.jpg and -s03.jpg: the App Store slides 01 and 03 of each app, per site language.

    python3 shots.py         # needs Pillow and the iOS checkouts in ~/Developer/iOS/<App>
    python3 build.py

Source: ~/Developer/iOS/<App>/docs/app-store/final/iphone-1206x2622/<lang>/0N.png (the composed store slides).
"""
import sys
from pathlib import Path

from PIL import Image

from strings import LANGS

ROOT = Path(__file__).parent
IOS = ROOT.parent / "iOS"
CHECKOUTS = {"payday": "TimeToPayday", "sub": "TimeToSub", "restructure": "TimeToRestructure", "event": "TimeToEvent"}
# Time to Event (nov 2026) ha le slide solo in italiano: le altre lingue usano quelle finché non ci sono.
FALLBACK = {"event": "it"}
SLIDES = ("01", "03")
WIDTH = 480


def main():
    missing = []
    for k, repo in CHECKOUTS.items():
        for lang in LANGS:
            for n in SLIDES:
                src = IOS / repo / "docs" / "app-store" / "final" / "iphone-1206x2622" / lang / f"{n}.png"
                if not src.exists() and k in FALLBACK:
                    src = IOS / repo / "docs" / "app-store" / "final" / "iphone-1206x2622" / FALLBACK[k] / f"{n}.png"
                if not src.exists():
                    missing.append(str(src))
                    continue
                im = Image.open(src).convert("RGB")
                im = im.resize((WIDTH, round(im.height * WIDTH / im.width)), Image.LANCZOS)
                out = ROOT / "assets" / "img" / lang / f"{k}-s{n}.jpg"
                out.parent.mkdir(parents=True, exist_ok=True)
                im.save(out, "JPEG", quality=82, optimize=True, progressive=True)
    if missing:
        sys.exit("missing slides:\n" + "\n".join(missing))
    print(f"{len(CHECKOUTS) * len(LANGS) * len(SLIDES)} screenshots written")


if __name__ == "__main__":
    main()
