# Changelog

All notable changes to this project will be documented in this file.

---

## [v2.2 "Petra"] - 2025-XX-XX (Upcoming)
### Added
- Additional performance optimizations.

### Changed
- UI refinements for a more modern look and improved interactivity.
- Updated filtering engine for even smoother performance on large datasets.

### Fixed
- Minor bugs reported in previous releases.
- Stability improvements for high-density CSV files.

---

## [v2.1 "Cappadocia"] - 2025-FEB-15
### Added
- **Zoom Functionality:** Implemented true zoom on the data display via a QGraphicsView/QGraphicsProxyWidget approach (or similar), allowing users to scale the entire table without merely adjusting the font.
- **Optimized Model Updates:** Blocked signals during CSV loading to minimize stuttering.
- **Enhanced Layout:** Introduced a scrollable filter panel and refined splitter stretch factors for a fixed-size, responsive layout.

### Changed
- Improved performance across filtering and sorting operations.
- Adjusted UI elements to ensure the left panel (data view) remains visible and responsive.

### Fixed
- Resolved issues where the application window would elongate excessively with many columns.
- Minor bug fixes in advanced filtering commands.

---

## [v2.0 "Red Rocks"] - 2025-FEB-11
### Added
- **Interactive Bundler ("BunMapP"):** An interactive tool for packaging DART as a standalone application, complete with saving/loading settings in proprietary `.bunmapp` files.
- **Cross-Platform Version Metadata:** Automatically generates a Windows version file or macOS Info.plist (via post-processing) based on user input.
- New PyInstaller options for universal bundling support.

### Changed
- Refactored code to streamline cross-platform bundling and version metadata generation.
- Enhanced CSV encoding detection and error handling.

### Fixed
- Resolved CSV loading errors related to non-UTF-8 encoded files.
- Fixed several issues with advanced filtering commands.

---

## [v1.2 "Joshua Tree"] - 2025-FEB-9
### Added
- **Dark Mode/Light Mode Toggle:** Introduced a stylish dark mode with an option to switch back to light mode.
- **Improved CSV Loading:** Integrated chardet for automatic encoding detection to support a variety of CSV formats.
- Smoother sorting and filtering interactions.

### Changed
- Enhanced overall UI responsiveness and stability.
- Updated layout adjustments for better space management.

### Fixed
- Addressed minor performance issues during CSV data processing.
- Corrected filtering bugs causing occasional mismatches.

---

## [v1.1 "Arches"] - 2025-FEB-8
### Added
- **Advanced Filtering Commands:**  
  - `#range: x,y` – Filter by numeric range.
  - `#startswith: text` – Match the beginning of cell text.
  - `#contains: text` – Perform a substring search.
  - `#equals: text` – Exact match filtering.
  - `#endswith: text` – Filter by text ending.
  - `#not: text` – Exclude rows containing certain text.
  - `#regex: pattern` – Regular expression filtering.
  - `#in: value1, value2, ...` – Filter by multiple exact values.
- Improved error handling for CSV decoding issues.

### Fixed
- Corrected problems with non-UTF8 CSV file loading.

---

## [v1.0 "Yosemite"] - 2025-FEB-7
### Added
- **Initial Release:**  
  - Basic CSV viewing with a table interface.
  - Simple case-insensitive substring filtering.
  - Sorting and exporting capabilities.
- Set up the foundation for advanced filtering and future enhancements.

---

*For a complete list of changes and to contribute, please see our [GitHub repository](https://github.com/alfaoz/dart).*
