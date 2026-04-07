# words

Word lists for typing practice, formatted as static HTML pages. Intended for use with [Monkeytype](https://monkeytype.com) (or a self-hosted instance) via the custom word list feature.

Live at: https://krisyotam.com/words/

## Regenerating

```
python3 build.py
```

Pure Python 3, no third-party dependencies. The script reads from `sources/` and writes HTML into the category directories.

## Sources

- **english/** -- [first20hours/google-10000-english](https://github.com/first20hours/google-10000-english) (MIT) and [monkeytypegame/monkeytype](https://github.com/monkeytypegame/monkeytype) (GPL-3.0)
- **code/** -- [monkeytypegame/monkeytype](https://github.com/monkeytypegame/monkeytype) (GPL-3.0)
- **specialty/** -- [monkeytypegame/monkeytype](https://github.com/monkeytypegame/monkeytype) (GPL-3.0)

Source data is vendored in `sources/` (no upstream `.git` history). Upstream commit SHAs are recorded in `sources/MANIFEST.txt`. License files from upstream repos are preserved in `sources/google-10000-english/` and `sources/monkeytype/`.
