# dart

load data, filter it, export it. that's it.

![screenshot](screenshot.png)

## what it does

a desktop data viewer. open a file, see it in a table, filter columns with commands, sort by clicking headers, export what you need. supports csv, tsv, json, and xlsx.

## filter commands

type these in the per-column filter inputs. prefix with `#`. without a prefix it does a case-insensitive substring search.

| command | what it does |
|---|---|
| `#range: x,y` | numeric range |
| `#startswith: text` | match beginning |
| `#contains: text` | substring search |
| `#equals: text` | exact match |
| `#endswith: text` | match ending |
| `#not: text` | exclude rows |
| `#regex: pattern` | regex |
| `#in: a, b, c` | match any value |

## keyboard shortcuts

| shortcut | action |
|---|---|
| `ctrl+o` | open file |
| `ctrl+shift+e` | export |
| `ctrl+f` | focus search |
| `ctrl+= / -` | zoom in/out |
| `ctrl+0` | reset zoom |
| `ctrl+i` | statistics |
| `ctrl+shift+t` | toggle theme |

## running it

```bash
git clone https://github.com/alfaoz/dart.git
cd dart
pip install -r requirements.txt
python main.py
```

requires python 3.9+.

you can also drag and drop files directly onto the window.

## how it's built

pyside6 for the ui. chardet for encoding detection. openpyxl for excel files. delimiter auto-detection via python's csv sniffer. everything runs locally, nothing leaves your machine.

the codebase is split into modules: `app.py` (main window), `theme.py` (colors + stylesheet), `filter_model.py` (filter logic), `dialogs.py` (about, help, stats), `widgets.py` (filter bar, search, overlays), `splash.py` (startup screen). `main.py` is just the entry point.

## ci/cd

push a tag and github actions builds standalone bundles for macos and windows via pyinstaller. artifacts are uploaded to the release.

## versions

dart uses rock-formation version names.

- **v1.0 "yosemite"** — initial release, basic csv viewing
- **v1.1 "arches"** — advanced filter commands, encoding detection
- **v1.2 "joshua tree"** — dark mode, improved loading
- **v2.0 "red rocks"** — interactive bundler, cross-platform packaging
- **v2.1 "cappadocia"** — zoom, optimized layout, scrollable filters
- **v2.2 "petra"** — full ui rewrite, multi-format support, modular codebase, ci builds

see [changelog.md](CHANGELOG.md) for details.

## contributing

found a bug? want a feature? open an issue or pr.

## license

mit
