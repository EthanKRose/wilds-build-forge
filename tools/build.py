"""Rebuild index.html from the game data.

Usage (from the repository root):
    python tools/build.py path/to/mhdb-wilds-data/output/merged [snapshot label]

Steps:
  1. Converts the mhdb-wilds-data merged JSON into a compact dataset (tools/build_data.py).
  2. Embeds that dataset into src/template.html and writes index.html.
"""
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    merged = os.path.abspath(sys.argv[1])
    label = sys.argv[2] if len(sys.argv) > 2 else "April 2026"
    with tempfile.TemporaryDirectory() as tmp:
        data_path = os.path.join(tmp, "data.json")
        subprocess.run(
            [sys.executable, os.path.join(ROOT, "tools", "build_data.py"), merged, data_path,
             os.path.join(ROOT, "data", "kinsects.json")],
            check=True,
        )
        with open(data_path, encoding="utf-8") as f:
            data = f.read().replace("</", "<\\/")
    with open(os.path.join(ROOT, "src", "template.html"), encoding="utf-8") as f:
        page = f.read()
    page = page.replace("__DATA__", data).replace("__DATE__", label)
    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as f:
        f.write(page)
    print(f"Wrote index.html ({len(page) // 1024} KB)")


if __name__ == "__main__":
    main()
