#!/usr/bin/env python3
"""
build.py -- generates static HTML for krisyotam/words
Run: python3 build.py

Reads source wordlists from sources/ and emits HTML into the repo root.
Idempotent: running twice produces identical output.
"""

import json
import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

ROOT = Path(__file__).parent.resolve()
SOURCES = ROOT / "sources"
GOOGLE = SOURCES / "google-10000-english"
MONKEYTYPE_LANGS = SOURCES / "monkeytype" / "frontend" / "static" / "languages"

# ---------------------------------------------------------------------------
# HTML helpers
# ---------------------------------------------------------------------------

HEAD_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="author" content="Kris Yotam">
  <link rel="stylesheet" href="{css_path}">
  <title>{title} -- Kris Yotam's Word Lists</title>
</head>
<body>
"""

FOOT = """\
</body>
</html>
"""


def css_path_for(depth: int) -> str:
    """Return root-relative CSS path suitable for a file at the given depth."""
    return "/words/style.css"


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


# ---------------------------------------------------------------------------
# Word-list page
# ---------------------------------------------------------------------------

def render_wordlist_page(
    title: str,
    words: list[str],
    source_label: str,
    category_slug: str,
    category_label: str,
) -> str:
    word_count = len(words)
    body = "\n".join(words)
    return (
        HEAD_TEMPLATE.format(css_path="/words/style.css", title=title)
        + f'<div class="text"><div class="left">\n'
        + f'<a class="back-link" href="/words/{category_slug}/">&larr; back to {category_label}</a>\n'
        + f"<h1>{title}</h1>\n"
        + f'<p class="wordlist-meta">{word_count:,} words &mdash; source: {source_label}</p>\n'
        + f'<pre class="wordlist">{body}</pre>\n'
        + "</div></div>\n"
        + FOOT
    )


# ---------------------------------------------------------------------------
# Category index page
# ---------------------------------------------------------------------------

def render_category_index(
    category_label: str,
    entries: list[tuple[str, str]],  # (slug, title)
) -> str:
    """entries is a list of (slug, human title) pairs."""
    listing_items = ""
    for slug, title in sorted(entries, key=lambda x: x[1].lower()):
        listing_items += (
            f'<div class="listing"><div class="left"><dl>'
            f'<dt><a href="{slug}.html">{title}</a></dt>'
            f"</dl></div></div>\n"
        )

    return (
        HEAD_TEMPLATE.format(css_path="/words/style.css", title=category_label)
        + f'<div class="text"><div class="left">\n'
        + f'<a class="back-link" href="/words/">&larr; back to word lists</a>\n'
        + f"<h1>{category_label}</h1>\n"
        + "</div></div>\n"
        + listing_items
        + FOOT
    )


# ---------------------------------------------------------------------------
# Root index page
# ---------------------------------------------------------------------------

def render_root_index(categories: list[tuple[str, str, str]]) -> str:
    """categories: list of (slug, label, description)"""
    listing_items = ""
    for slug, label, desc in categories:
        listing_items += (
            f'<div class="listing"><div class="left"><dl>'
            f'<dt><a href="/words/{slug}/">{label}</a>'
            + (f" <i>{desc}</i>" if desc else "")
            + f"</dt></dl></div></div>\n"
        )

    return (
        HEAD_TEMPLATE.format(css_path="/words/style.css", title="Word Lists")
        + '<div class="text"><div class="left">\n'
        + "<h1>Kris Yotam's Word Lists</h1>\n"
        + "<p>Curated word lists for typing practice. Paste any list into "
        + '<a href="https://monkeytype.com">Monkeytype</a> (or a self-hosted instance) '
        + "to use as a custom word set.</p>\n"
        + "<p>&mdash; <a href=\"https://krisyotam.com/home\">Kris</a></p>\n"
        + "</div></div>\n"
        + listing_items
        + FOOT
    )


# ---------------------------------------------------------------------------
# Placeholder page
# ---------------------------------------------------------------------------

def render_placeholder(label: str, note: str) -> str:
    return (
        HEAD_TEMPLATE.format(css_path="/words/style.css", title=label)
        + f'<div class="text"><div class="left">\n'
        + f'<a class="back-link" href="/words/">&larr; back to word lists</a>\n'
        + f"<h1>{label}</h1>\n"
        + f'<p class="coming-soon">{note}</p>\n'
        + "</div></div>\n"
        + FOOT
    )


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def load_google_txt(filepath: Path) -> list[str]:
    return [l.strip() for l in filepath.read_text(encoding="utf-8").splitlines() if l.strip()]


def load_monkeytype_json(filepath: Path) -> list[str]:
    data = json.loads(filepath.read_text(encoding="utf-8"))
    return [w.strip() for w in data.get("words", []) if w.strip()]


def mt_path(filename: str) -> Path:
    return MONKEYTYPE_LANGS / filename


def mt_exists(filename: str) -> bool:
    return mt_path(filename).exists()


# ---------------------------------------------------------------------------
# English category
# ---------------------------------------------------------------------------

def build_english(manifest: list[str]) -> list[tuple[str, str]]:
    """Returns list of (slug, title) for the category index."""
    entries: list[tuple[str, str]] = []
    cat = "english"
    cat_label = "English"

    specs = [
        # (slug, title, loader_fn)
        ("1k",   "English 1k",                   lambda: load_monkeytype_json(mt_path("english_1k.json"))),
        ("5k",   "English 5k",                   lambda: load_monkeytype_json(mt_path("english_5k.json"))),
        ("10k",  "English 10k",                  lambda: load_monkeytype_json(mt_path("english_10k.json"))),
        ("25k",  "English 25k",                  lambda: load_monkeytype_json(mt_path("english_25k.json"))),
        ("full", "English (Google 10k)",          lambda: load_google_txt(GOOGLE / "google-10000-english.txt")),
        ("20k",  "English 20k (Google)",          lambda: load_google_txt(GOOGLE / "20k.txt")),
        ("no-swears",     "English No Swears",    lambda: load_google_txt(GOOGLE / "google-10000-english-no-swears.txt")),
        ("usa",           "English USA",          lambda: load_google_txt(GOOGLE / "google-10000-english-usa.txt")),
        ("usa-no-swears", "English USA No Swears",lambda: load_google_txt(GOOGLE / "google-10000-english-usa-no-swears.txt")),
        ("long",          "English Long Words",   lambda: load_google_txt(GOOGLE / "google-10000-english-usa-no-swears-long.txt")),
        ("medium",        "English Medium Words", lambda: load_google_txt(GOOGLE / "google-10000-english-usa-no-swears-medium.txt")),
        ("short",         "English Short Words",  lambda: load_google_txt(GOOGLE / "google-10000-english-usa-no-swears-short.txt")),
        ("misspelled",    "Commonly Misspelled",  lambda: load_monkeytype_json(mt_path("english_commonly_misspelled.json"))),
        ("doubled",       "Double-Letter Words",  lambda: load_monkeytype_json(mt_path("english_doubleletter.json"))),
        ("contractions",  "Contractions",         lambda: load_monkeytype_json(mt_path("english_contractions.json"))),
        ("old",           "Old English",          lambda: load_monkeytype_json(mt_path("english_old.json"))),
        ("shakespearean", "Shakespearean",        lambda: load_monkeytype_json(mt_path("english_shakespearean.json"))),
    ]

    source_map = {
        "full":           "first20hours/google-10000-english (MIT)",
        "20k":            "first20hours/google-10000-english (MIT)",
        "no-swears":      "first20hours/google-10000-english (MIT)",
        "usa":            "first20hours/google-10000-english (MIT)",
        "usa-no-swears":  "first20hours/google-10000-english (MIT)",
        "long":           "first20hours/google-10000-english (MIT)",
        "medium":         "first20hours/google-10000-english (MIT)",
        "short":          "first20hours/google-10000-english (MIT)",
    }

    for slug, title, loader in specs:
        source_label = source_map.get(slug, "monkeytypegame/monkeytype (GPL-3.0)")
        try:
            words = loader()
        except FileNotFoundError:
            manifest.append(f"SKIP english/{slug} -- file not found")
            continue
        if not words:
            manifest.append(f"SKIP english/{slug} -- empty wordlist")
            continue

        html = render_wordlist_page(title, words, source_label, cat, cat_label)
        write_file(ROOT / cat / f"{slug}.html", html)
        entries.append((slug, title))
        manifest.append(f"OK   english/{slug}.html  ({len(words):,} words)")

    return entries


# ---------------------------------------------------------------------------
# Code category
# ---------------------------------------------------------------------------

def build_code(manifest: list[str]) -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    cat = "code"
    cat_label = "Code"
    source_label = "monkeytypegame/monkeytype (GPL-3.0)"

    # Collect all code_*.json files (prefer non-1k/2k/5k variants as primary,
    # but include numbered variants too with a disambiguating slug)
    lang_dir = MONKEYTYPE_LANGS
    code_files = sorted(lang_dir.glob("code_*.json"))

    for filepath in code_files:
        name = filepath.stem  # e.g. "code_python" or "code_python_1k"
        # Build a readable slug from the filename
        slug = name.removeprefix("code_")
        # Map special chars for filesystem safety (already safe in filenames, but slugify)
        slug = slug.replace("+", "p").replace("#", "sharp").replace(" ", "_")
        # Human-readable title
        title = slug.replace("_", " ").replace("p p", "++").title()
        # Fix up some common names
        title_fixes = {
            "C": "C",
            "Cpp": "C++",
            "Csharp": "C#",
            "Csharp 1K": "C# 1k",
            "Javascript": "JavaScript",
            "Javascript 1K": "JavaScript 1k",
            "Javascript React": "JavaScript React",
            "Typescript": "TypeScript",
            "Python 1K": "Python 1k",
            "Python 2K": "Python 2k",
            "Python 5K": "Python 5k",
            "R 2K": "R 2k",
            "Abap 1K": "ABAP 1k",
            "Abap": "ABAP",
            "Arduino": "Arduino",
            "Assembly": "Assembly",
            "Bash": "Bash",
            "Brainfck": "Brainfuck",
            "Clojure": "Clojure",
            "Cobol": "COBOL",
            "Common Lisp": "Common Lisp",
            "Css": "CSS",
            "Cuda": "CUDA",
            "Dart": "Dart",
            "Elixir": "Elixir",
            "Erlang": "Erlang",
            "Fortran": "Fortran",
            "Fsharp": "F#",
            "Gdscript": "GDScript",
            "Gdscript 2": "GDScript 2",
            "Gleam": "Gleam",
            "Go": "Go",
            "Haskell": "Haskell",
            "Html": "HTML",
            "Java": "Java",
            "Jule": "Jule",
            "Julia": "Julia",
            "Kotlin": "Kotlin",
            "Latex": "LaTeX",
            "Lua": "Lua",
            "Luau": "Luau",
            "Matlab": "MATLAB",
            "Nim": "Nim",
            "Nix": "Nix",
            "Ocaml": "OCaml",
            "Odin": "Odin",
            "Ook": "Ook",
            "Opencl": "OpenCL",
            "Pascal": "Pascal",
            "Perl": "Perl",
            "Php": "PHP",
            "Powershell": "PowerShell",
            "Python": "Python",
            "R": "R",
            "Rockstar": "Rockstar",
            "Ruby": "Ruby",
            "Rust": "Rust",
            "Scala": "Scala",
            "Sql": "SQL",
            "Swift": "Swift",
            "Systemverilog": "SystemVerilog",
            "Typescript": "TypeScript",
            "Typst": "Typst",
            "V": "V",
            "Vim": "Vim",
            "Vimscript": "VimScript",
            "Visual Basic": "Visual Basic",
            "Yoptascript": "YoptaScript",
            "Zig": "Zig",
        }
        title = title_fixes.get(title, title)

        try:
            words = load_monkeytype_json(filepath)
        except Exception as e:
            manifest.append(f"SKIP code/{slug} -- {e}")
            continue
        if not words:
            manifest.append(f"SKIP code/{slug} -- empty")
            continue

        html = render_wordlist_page(f"Code: {title}", words, source_label, cat, cat_label)
        write_file(ROOT / cat / f"{slug}.html", html)
        entries.append((slug, f"Code: {title}"))
        manifest.append(f"OK   code/{slug}.html  ({len(words):,} words)")

    return entries


# ---------------------------------------------------------------------------
# Specialty category
# ---------------------------------------------------------------------------

def build_specialty(manifest: list[str]) -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    cat = "specialty"
    cat_label = "Specialty"
    source_label = "monkeytypegame/monkeytype (GPL-3.0)"

    specs = [
        ("medical",      "Medical Terminology",        "english_medical.json"),
        ("english-450k", "English 450K (full lexicon)","english_450k.json"),
    ]

    # Also scan for any other monkeytype files that don't fit english or code
    # (future-proofing)

    for slug, title, filename in specs:
        if not mt_exists(filename):
            manifest.append(f"SKIP specialty/{slug} -- {filename} not found")
            continue
        try:
            words = load_monkeytype_json(mt_path(filename))
        except Exception as e:
            manifest.append(f"SKIP specialty/{slug} -- {e}")
            continue
        if not words:
            manifest.append(f"SKIP specialty/{slug} -- empty")
            continue

        html = render_wordlist_page(title, words, source_label, cat, cat_label)
        write_file(ROOT / cat / f"{slug}.html", html)
        entries.append((slug, title))
        manifest.append(f"OK   specialty/{slug}.html  ({len(words):,} words)")

    return entries


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    manifest: list[str] = []

    print("Building english/ ...")
    english_entries = build_english(manifest)
    write_file(
        ROOT / "english" / "index.html",
        render_category_index("English Word Lists", english_entries),
    )

    print("Building code/ ...")
    code_entries = build_code(manifest)
    write_file(
        ROOT / "code" / "index.html",
        render_category_index("Code Word Lists", code_entries),
    )

    print("Building specialty/ ...")
    specialty_entries = build_specialty(manifest)
    write_file(
        ROOT / "specialty" / "index.html",
        render_category_index("Specialty Word Lists", specialty_entries),
    )

    print("Building symbols/ placeholder ...")
    write_file(
        ROOT / "symbols" / "index.html",
        render_placeholder(
            "Symbol Drills",
            "Coming soon -- LLM-generated symbol drills.",
        ),
    )

    print("Building drills/ placeholder ...")
    write_file(
        ROOT / "drills" / "index.html",
        render_placeholder(
            "Drills",
            "Coming soon -- LLM-generated symbol drills.",
        ),
    )

    print("Building root index.html ...")
    categories = [
        ("english",   "English",   "frequency lists, filtered variants"),
        ("code",      "Code",      "language tokens from monkeytype"),
        ("specialty", "Specialty", "medical and domain-specific"),
        ("symbols",   "Symbols",   "coming soon"),
        ("drills",    "Drills",    "coming soon"),
    ]
    write_file(ROOT / "index.html", render_root_index(categories))

    # Write manifest
    manifest_path = SOURCES / "MANIFEST.txt"
    manifest_header = [
        "# words -- source manifest",
        "# Generated by build.py",
        "",
        "## Upstream commit SHAs",
        "# google-10000-english: d0736d492489198e4f9d650c7ab4143bc14c1e9e",
        "# monkeytype:           ab085e2cb73e0e806f8790408c9042ef87d8ece4",
        "",
        "## Files",
    ]
    manifest_path.write_text(
        "\n".join(manifest_header + manifest) + "\n", encoding="utf-8"
    )

    ok_count = sum(1 for m in manifest if m.startswith("OK"))
    skip_count = sum(1 for m in manifest if m.startswith("SKIP"))
    print(f"\nDone. {ok_count} word-list pages generated, {skip_count} skipped.")
    print(f"Manifest written to {manifest_path}")


if __name__ == "__main__":
    main()
