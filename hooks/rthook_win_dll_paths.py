"""Runtime hook: make Windows DLL lookup reliable for PySide6 frozen apps."""

import os
import sys


def _resolve_base_dir() -> str:
    """Return folder that contains frozen app binaries."""
    base = getattr(sys, "_MEIPASS", "")
    if base:
        return base

    # Fallback for non-frozen runs or unusual launchers.
    exe_dir = os.path.dirname(sys.executable)
    internal_dir = os.path.join(exe_dir, "_internal")
    return internal_dir if os.path.isdir(internal_dir) else exe_dir


if sys.platform == "win32":
    base_dir = _resolve_base_dir()
    dll_dirs = [
        base_dir,
        os.path.join(base_dir, "PySide6"),
        os.path.join(base_dir, "shiboken6"),
    ]
    for path in dll_dirs:
        if not os.path.isdir(path):
            continue
        try:
            os.add_dll_directory(path)
        except (AttributeError, OSError):
            # Ignore if unsupported or path registration fails.
            pass
