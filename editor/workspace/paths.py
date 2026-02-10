# Where to store the workspaces? How to calculate their IDs?
from __future__ import annotations
from encodings.punycode import T
import hashlib
from logging import root
import string
from PySide6.QtCore import QStandardPaths
from pathlib import Path
from dataclasses import dataclass

import uuid

# ---------- App Identity ----------

def ensure_app_identity(org_name: str, app_name: str) -> None:
    """
    Ensures that Qt knows the name of the organisation and application.
    This affects the AppLocalDataLocation path (AppData\Local\<Org>\<App>).
    Call once at programme start-up, before any QStandardPaths calls.
    """
    from PySide6.QtCore import QCoreApplication
    QCoreApplication.setOrganizationName(org_name)
    QCoreApplication.setApplicationName(app_name)

# ---------- Roots ----------

def app_local_data_root() -> Path:
    "Root directory of the application (Windows: AppData\Local\<Org>\<App>)."
    path = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppLocalDataLocation)
    if not path:
        raise RuntimeError("Qt did not return the AppLocalDataLocation path.")
    return Path(path)

def ensure_base_dirs() -> AppDirs:
    """
    Creates the application's base folders (workspaces/backups/logs/recovery) and returns them.
    Call at startup or before the first operation with a workspace.
    """
    root = app_local_data_root()
    dirs = AppDirs(
        root=root,
        workspaces=root / "workspaces",
        backups=root / "backups",
        recovery=root / "recovery",
        logs=root / "logs",
    )

    for directory in (dirs.workspaces, dirs.recovery, dirs.logs):
        directory.mkdir(parents=True, exist_ok=True)
    return dirs

@dataclass(frozen=True)
class AppDirs:
    root: Path
    workspaces: Path
    backups: Path
    recovery: Path
    logs: Path

# ---------- Project Key | Workspace Layout ----------

def new_project_uid() -> str:
    """
    Generates a permanent project_uid (UUIDv4) for writing to meta/manifest.json.
    It is recommended to use it as the workspace key (more stable than the file path).
    """
    return str(uuid.uuid4())

def isUUID(s: str) -> bool:
    try:
        uuid.UUID(s)
        return True
    except Exception:
        return False

def project_key(project_uid: str | None, container_path: str | Path | None = None) -> str:
    """
    Returns the stable key for the workspace folder.
    Preference: project_uid (UUID).
    Fallback: hash from the absolute path to .cldl (if project_uid is not yet available).
    """
    if project_uid and isUUID(project_uid):
        return project_uid
    if container_path is None:
        raise ValueError("You need either project_uid or container_path to calculate the key.")
    absolute_path = str(Path(container_path).resolve())
    digest = hashlib.sha256(absolute_path.encode("utf-8")).hexdigest()[:16]
    return f"path_{digest}"

def workspace_root(project_uid: str | None, container_path: str | Path | None = None) -> Path:
    """
    Returns the workspace root of the given project
    <AppLocalData>/workspaces/<project_key>/
    """
    dirs = ensure_base_dirs()
    key = project_key(project_uid, container_path)
    path = dirs.workspaces / key
    path.mkdir(parents=True, exist_ok=True)
    return path

def unpacked_dir(project_uid: str | None, container_path: str | Path | None = None) -> Path:
    """
    Folder with an unpacked CLDL structure:
    <workspace_root>/unpacked/
    """
    path = workspace_root(project_uid, container_path) / "unpacked"
    path.mkdir(parents=True, exist_ok=True)
    return path

def lock_path(project_uid: str | None, container_path: str | Path | None = None) -> Path:
    """
    Lock file created in a workspace
    """
    return workspace_root(project_uid, container_path) / "lock.json"

def session_path(project_uid: str | None, container_path: str | Path | None = None) -> Path:
    """
    Session metadata (what is open, when, what format version, etc.)
    """
    return workspace_root(project_uid, container_path) / "session.json"

def pack_temp_path(container_path: str | Path) -> Path:
    """
    The path of the temporary file for atomic packaging:
    <workspace_root>/tmp/<name>.tmp.cldl
    """
    cp = Path(container_path)
    tmp_dir = ensure_base_dirs().root / "tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    return tmp_dir / f"{cp.stem}.tmp.cldl"

def debug_paths() -> None:
    """
    Debug helper for editor/workspace/paths.py.
    Prints all key paths and derived values.

    Usage (e.g. from main after QApplication is created):
        ensure_app_identity("ChiharaYakou", "CLDL Editor")
        debug_paths()
    """
    import sys
    from pathlib import Path

    # Ensure Qt has an application instance (QStandardPaths may depend on it)
    try:
        from PySide6.QtCore import QCoreApplication
        app = QCoreApplication.instance()
        if app is None:
            _ = QCoreApplication(sys.argv)
    except Exception as e:
        print("[debug_paths] Warning: failed to ensure QCoreApplication:", e)

    print("\n=== debug_paths ===")

    # App identity
    try:
        from PySide6.QtCore import QCoreApplication
        print("Organization:", QCoreApplication.organizationName())
        print("Application :", QCoreApplication.applicationName())
    except Exception as e:
        print("[debug_paths] Could not read app identity:", e)

    # Root + base dirs
    try:
        root = app_local_data_root()
        print("AppLocalData root:", root)
    except Exception as e:
        print("[debug_paths] app_local_data_root() failed:", e)
        root = None

    try:
        dirs = ensure_base_dirs()
        print("\n-- Base dirs --")
        print("root      :", dirs.root)
        print("workspaces:", dirs.workspaces)
        print("backups   :", dirs.backups)
        print("recovery  :", dirs.recovery)
        print("logs      :", dirs.logs)
    except Exception as e:
        print("[debug_paths] ensure_base_dirs() failed:", e)
        dirs = None

    # Sample keys/paths
    try:
        sample_uid = new_project_uid()
    except Exception:
        sample_uid = None

    print("\n-- Workspace derivations (sample) --")
    try:
        if sample_uid:
            print("sample project_uid:", sample_uid)
            print("project_key(uid)  :", project_key(sample_uid))
            print("workspace_root    :", workspace_root(sample_uid))
            print("unpacked_dir      :", unpacked_dir(sample_uid))
            print("lock_path         :", lock_path(sample_uid))
            print("session_path      :", session_path(sample_uid))
    except Exception as e:
        print("[debug_paths] Workspace derivations failed:", e)

    # Fallback key from a container path
    print("\n-- Fallback key (container path) --")
    try:
        # Change this to a real .cldl path if you want deterministic output.
        fake_container = Path.cwd() / "sample.cldl"
        print("fake container path:", fake_container)
        print("project_key(path)  :", project_key(None, fake_container))
        print("pack_temp_path     :", pack_temp_path(fake_container))
    except Exception as e:
        print("[debug_paths] Fallback key derivation failed:", e)

    print("=== end debug_paths ===\n")
