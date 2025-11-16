from __future__ import annotations

from pathlib import Path
from typing import List, Tuple


def _resolve_session_glob(
    session_name: str,
    workdir: str | Path | None = None,
) -> Tuple[Path, str]:
    """Return the directory and filename prefix for the session artifacts."""
    base_dir = Path(workdir) if workdir else Path.cwd()
    raw_path = Path(session_name)

    if raw_path.is_absolute():
        base_dir = raw_path.parent
        prefix = raw_path.name
    else:
        if raw_path.parent != Path('.'):
            base_dir = (Path(workdir) if workdir else Path.cwd()) / raw_path.parent
            prefix = raw_path.name
        else:
            prefix = raw_path.name or "pyrogram"
            base_dir = Path(workdir) if workdir else base_dir

    if not prefix.endswith(".session"):
        prefix = f"{prefix}.session"

    return base_dir, prefix


def purge_session_artifacts(
    session_name: str,
    workdir: str | Path | None = None,
) -> List[Path]:
    """Delete Pyrogram session files (including WAL/JOURNAL) and return the removed paths."""
    base_dir, prefix = _resolve_session_glob(session_name, workdir)

    if not base_dir.exists():
        return []

    removed: List[Path] = []
    for file_path in base_dir.glob(f"{prefix}*"):
        if file_path.is_file():
            file_path.unlink()
            removed.append(file_path)

    return removed


def reset_stale_session(session_name: str, workdir: str | Path | None = None) -> List[Path]:
    """Convenience wrapper to purge artifacts and return what was removed."""
    return purge_session_artifacts(session_name=session_name, workdir=workdir)
