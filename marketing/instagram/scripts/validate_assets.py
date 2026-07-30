#!/usr/bin/env python3
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
EXPORT = ROOT / "export"
EXPECTED = {
    "feed": (12, (1080, 1350)),
    "carousel-01": (4, (1080, 1350)),
    "stories": (8, (1080, 1920)),
    "reels": (4, (1080, 1920)),
    "profile/highlights": (7, (1080, 1080)),
}
errors = []
for folder, (count, size) in EXPECTED.items():
    files = sorted((EXPORT / folder).glob("*.png"))
    if len(files) != count:
        errors.append(f"{folder}: esperado {count}, encontrado {len(files)}")
    for path in files:
        with Image.open(path) as image:
            if image.size != size:
                errors.append(f"{path}: dimensão {image.size}, esperado {size}")
avatar = EXPORT / "profile/avatar.png"
with Image.open(avatar) as image:
    if image.size != (1080, 1080):
        errors.append("avatar fora de 1080x1080")
if errors:
    raise SystemExit("VALIDATION_FAILED\n" + "\n".join(errors))
print("VALIDATION_OK client=Prático Soluções assets=36")
