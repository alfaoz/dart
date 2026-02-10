# changelog

## v2.2 "petra" - 2026-feb-10 (latest)

### added
- full ui rewrite: modern minimal design with green color scheme from logo
- multi-format support: csv, tsv, json, xlsx import and export
- delimiter auto-detection for text files (comma, semicolon, tab, pipe)
- splash screen on startup with logo
- loading overlay during data import
- inline column filter bar replacing the old right sidebar
- native widget-based help dialog
- stats export to csv
- drag and drop for all supported file formats
- keyboard shortcuts for all major actions
- github actions ci pipeline for macos and windows builds

### changed
- restructured from single main.py into modular codebase
- theme system with color tokens replacing hardcoded stylesheets
- table is now full-width, no more splitter layout
- action bar with grouped buttons replacing text-only toolbar

### fixed
- column resize no longer causes window to grow unbounded
- filter bar properly clips and scrolls with the table

---

## v2.1 "cappadocia" - 2025-feb-15

### added
- zoom functionality for scaling the table display
- optimized model updates by blocking signals during csv loading
- scrollable filter panel with refined layout

### changed
- improved filtering and sorting performance
- adjusted ui elements for better responsiveness

### fixed
- window no longer elongates with many columns
- minor filter command bugs

---

## v2.0 "red rocks" - 2025-feb-11

### added
- interactive bundler (bunmapp) for standalone packaging
- cross-platform version metadata generation
- pyinstaller bundling support

### changed
- refactored bundling and metadata code
- enhanced encoding detection

### fixed
- csv loading errors with non-utf-8 files
- several filter command issues

---

## v1.2 "joshua tree" - 2025-feb-9

### added
- dark/light mode toggle
- chardet integration for encoding detection
- smoother sorting and filtering

### fixed
- performance issues during csv processing
- filtering mismatches

---

## v1.1 "arches" - 2025-feb-8

### added
- advanced filter commands: range, startswith, contains, equals, endswith, not, regex, in
- improved csv decoding error handling

### fixed
- non-utf8 csv loading

---

## v1.0 "yosemite" - 2025-feb-7

### added
- initial release
- basic csv viewing, substring filtering, sorting, exporting
