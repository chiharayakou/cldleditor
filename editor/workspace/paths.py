# Where to store the workspaces? How to calculate their IDs?
from logging import root
import string
from PySide6.QtCore import QCoreApplication, QStandardPaths
from pathlib import Path
from __future__ import annotations
from dataclasses import dataclass

import uuid

# ---------- App Identity ----------

def ensure_app_identity(org_name: str, app_name: str) -> None:
    """
    Ensures that Qt knows the name of the organisation and application.
    This affects the AppLocalDataLocation path (AppData\Local\<Org>\<App>).
    Call once at programme start-up, before any QStandardPaths calls.
    """
    if not QCoreApplication.organizationName():
        QCoreApplication.setOrganizationName(org_name)
    if not QCoreApplication.applicationName():
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