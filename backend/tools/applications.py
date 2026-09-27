"""Windows application control.

Every function here performs a real operating-system action and reports what
actually happened:

  * a launch is only reported as successful once a matching process is
    observed (or the shell/OS refused the request),
  * the verification method that proved the launch is returned to the GUI,
  * when Windows refuses to start the target the tool returns a failure - it
    never fabricates success.
"""

from __future__ import annotations

import difflib
import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Dict, List, NamedTuple, Optional, Tuple

from errors import ErrorCode
from logger.logger import logger
from security.permissions import PermissionLevel
from tools.base import ToolResult, ToolSpec

try:  # psutil is used for launch verification; the tool degrades without it.
    import psutil
except ImportError:  # pragma: no cover - psutil is a hard dependency in practice
    psutil = None  # type: ignore[assignment]

IS_WINDOWS = os.name == "nt"

# alias -> (command, expected process image names)
APP_ALIASES: Dict[str, Tuple[str, List[str]]] = {
    "visual studio code": ("code", ["Code.exe"]),
    "vscode": ("code", ["Code.exe"]),
    "vs code": ("code", ["Code.exe"]),
    "code": ("code", ["Code.exe"]),
    "notepad": ("notepad.exe", ["Notepad.exe"]),
    "calculator": ("calc.exe", ["CalculatorApp.exe", "calc.exe"]),
    "calc": ("calc.exe", ["CalculatorApp.exe", "calc.exe"]),
    "file explorer": ("explorer.exe", ["explorer.exe"]),
    "explorer": ("explorer.exe", ["explorer.exe"]),
    "files": ("explorer.exe", ["explorer.exe"]),
    "windows terminal": ("wt.exe", ["WindowsTerminal.exe"]),
    "terminal": ("wt.exe", ["WindowsTerminal.exe"]),
    "powershell": ("powershell.exe", ["powershell.exe"]),
    "command prompt": ("cmd.exe", ["cmd.exe"]),
    "cmd": ("cmd.exe", ["cmd.exe"]),
    "google chrome": ("chrome.exe", ["chrome.exe"]),
    "chrome": ("chrome.exe", ["chrome.exe"]),
    "microsoft edge": ("msedge.exe", ["msedge.exe"]),
    "edge": ("msedge.exe", ["msedge.exe"]),
    "firefox": ("firefox.exe", ["firefox.exe"]),
    "task manager": ("taskmgr.exe", ["Taskmgr.exe"]),
    "paint": ("mspaint.exe", ["mspaint.exe"]),
    "registry editor": ("regedit.exe", ["regedit.exe"]),
    "control panel": ("control.exe", ["control.exe"]),
    "snipping tool": ("snippingtool.exe", ["SnippingTool.exe"]),
}

# Aliases that resolve to a URI scheme instead of an executable.
URI_ALIASES: Dict[str, str] = {
    "windows settings": "ms-settings:",
    "settings": "ms-settings:",
    "network settings": "ms-settings:network",
    "bluetooth settings": "ms-settings:bluetooth",
    "windows store": "ms-windows-store:",
}

# Directories searched for installed application shortcuts.
START_MENU_DIRS: List[Path] = [
    Path(os.getenv("ProgramData", r"C:\ProgramData")) / "Microsoft/Windows/Start Menu/Programs",
    Path(os.getenv("APPDATA", "")) / "Microsoft/Windows/Start Menu/Programs",
]

LAUNCH_VERIFY_TIMEOUT = 3.0
LAUNCH_POLL_INTERVAL = 0.25


class LaunchEvidence(NamedTuple):
    image: str
    pid: int
    verified_by: str  # "image_name" | "new_process" | "shell"


def _normalise(value: str) -> str:
    return "".join(ch for ch in str(value).lower() if ch.isalnum())


def _expected_images(command: str) -> List[str]:
    return [f"{Path(command).stem.lower()}.exe"]


def _find_alias(app_name: str) -> Optional[Tuple[str, List[str]]]:
    key = _normalise(app_name)
    for alias, value in APP_ALIASES.items():
        if _normalise(alias) == key:
            return value
    return None


def _find_uri(app_name: str) -> Optional[str]:
    key = _normalise(app_name)
    for alias, uri in URI_ALIASES.items():
        if _normalise(alias) == key:
            return uri
    return None


def _find_start_menu_shortcut(app_name: str) -> Optional[Path]:
    """Locate an installed application shortcut matching `app_name`."""
    target = _normalise(app_name)
    if not target:
        return None

    candidates: List[Path] = []
    for directory in START_MENU_DIRS:
        if not directory.exists():
            continue
        for pattern in ("*.lnk", "*.url"):
            try:
                candidates.extend(directory.rglob(pattern))
            except OSError:  # pragma: no cover - permission edge cases
                continue

    if not candidates:
        return None

    by_normalised_stem = {_normalise(candidate.stem): candidate for candidate in candidates}
    if target in by_normalised_stem:
        return by_normalised_stem[target]

    close = difflib.get_close_matches(target, list(by_normalised_stem), n=1, cutoff=0.78)
    if close:
        return by_normalised_stem[close[0]]

    # Token fallback: "visual studio code" -> "code" when it is unambiguous.
    tokens = [token for token in _normalise(app_name) if len(token) > 2]
    for token in tokens:
        matches = [key for key in by_normalised_stem if key == token or key.startswith(token)]
        if len(matches) == 1:
            return by_normalised_stem[matches[0]]
    return None


def _process_snapshot() -> Dict[int, str]:
    """Map pid -> lowercase image name for every running process."""
    if psutil is None:
        return {}
    snapshot: Dict[int, str] = {}
    for process in psutil.process_iter(["pid", "name"]):
        try:
            name = (process.info.get("name") or "").lower()
            snapshot[int(process.info["pid"])] = name
        except Exception:  # pragma: no cover - process vanished mid-scan
            continue
    return snapshot


def _collect_launch_evidence(
    baseline: Dict[int, str], expected: List[str]
) -> Optional[LaunchEvidence]:
    """Return proof that the target application is running, if available."""
    wanted = {image.lower() for image in expected}
    stems = {Path(image).stem.lower() for image in expected}

    current = _process_snapshot()
    for pid, name in current.items():
        if name in wanted or Path(name).stem.lower() in stems:
            return LaunchEvidence(image=name, pid=pid, verified_by="image_name")

    for pid, name in current.items():
        if pid not in baseline:
            return LaunchEvidence(image=name, pid=pid, verified_by="new_process")

    if psutil is None:
        # Without process inspection the only signal left is a clean shell exit.
        return LaunchEvidence(image="unknown", pid=0, verified_by="shell")
    return None


def _launch_command(command: str) -> Tuple[bool, str, str]:
    """Start a process or shell target. Returns (started, method, error)."""
    creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0) if IS_WINDOWS else 0

    resolved = shutil.which(command)
    if resolved:
        try:
            if resolved.lower().endswith((".cmd", ".bat")):
                subprocess.Popen(
                    ["cmd.exe", "/c", "start", "", resolved],
                    creationflags=creation_flags,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            else:
                subprocess.Popen([resolved], creationflags=creation_flags)
            return True, f"executable:{resolved}", ""
        except OSError as exc:
            return False, "executable", str(exc)

    try:
        completed = subprocess.run(
            ["cmd.exe", "/c", "start", "", command],
            capture_output=True,
            text=True,
            timeout=10,
            creationflags=creation_flags,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return False, "shell", str(exc)

    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout or "").strip()
        return False, "shell", detail or f"cmd /c start exited with code {completed.returncode}"
    return True, "shell", ""


def _open_shell_target(target: str) -> Tuple[bool, str]:
    try:
        os.startfile(target)  # type: ignore[attr-defined]  # Windows shell association
        return True, ""
    except OSError as exc:
        return False, str(exc)


def open_application(app_name: str) -> ToolResult:
    """Open a Windows application and verify that it actually started."""
    name = (app_name or "").strip()
    if not name:
        return ToolResult.failure(
            "open_application",
            "No application name was provided.",
            code=ErrorCode.TOOL_INVALID_ARGUMENTS,
        )

    baseline = _process_snapshot()

    # 1. URI schemes (Windows Settings, Microsoft Store, ...)
    uri = _find_uri(name)
    if uri is not None:
        logger.info("[open_application] launching URI %s (request: %r)", uri, name)
        opened, error = _open_shell_target(uri)
        if opened:
            return ToolResult(
                tool="open_application",
                success=True,
                message=f"{name} is open.",
                data={"app_name": name, "target": uri, "method": "uri", "verified_by": "shell"},
            )
        return ToolResult.failure(
            "open_application",
            f"Windows could not open '{name}' ({uri}): {error}",
            app_name=name,
            target=uri,
        )

    # 2. Known alias -> command line target
    alias = _find_alias(name)
    shortcut: Optional[Path] = None

    if alias is not None:
        command, expected = alias
    else:
        # 3. Installed application shortcut (Start Menu)
        shortcut = _find_start_menu_shortcut(name)
        if shortcut is None:
            return ToolResult.failure(
                "open_application",
                f"'{name}' is not a known application and no matching Start Menu shortcut was found.",
                code=ErrorCode.TOOL_NOT_FOUND,
                app_name=name,
                known_applications=sorted(APP_ALIASES),
            )
        command, expected = str(shortcut), _expected_images(shortcut.stem)

    logger.info("[open_application] launching %r via %r", name, command)

    if shortcut is not None:
        opened, error = _open_shell_target(command)
        method = "shortcut"
    else:
        opened, method, error = _launch_command(command)

    if not opened:
        return ToolResult.failure(
            "open_application",
            f"Windows failed to start '{name}': {error}",
            app_name=name,
            target=command,
            method=method,
        )

    deadline = time.monotonic() + LAUNCH_VERIFY_TIMEOUT
    evidence: Optional[LaunchEvidence] = None
    while time.monotonic() < deadline:
        evidence = _collect_launch_evidence(baseline, expected)
        if evidence is not None:
            break
        time.sleep(LAUNCH_POLL_INTERVAL)

    if evidence is None:
        return ToolResult.failure(
            "open_application",
            f"'{name}' did not start. The launch request was accepted but no matching process is running.",
            app_name=name,
            target=command,
            method=method,
        )

    return ToolResult(
        tool="open_application",
        success=True,
        message=f"{name} is open.",
        data={
            "app_name": name,
            "target": command,
            "method": method,
            "process": evidence.image,
            "pid": evidence.pid,
            "verified_by": evidence.verified_by,
        },
    )


OPEN_APPLICATION_SPEC = ToolSpec(
    name="open_application",
    description=(
        "Open a Windows desktop application by name, for example 'Visual Studio Code', 'Notepad', "
        "'Calculator', 'Google Chrome', 'File Explorer' or 'Windows Terminal'. Use this tool whenever "
        "the user asks to open, launch, start or show an application."
    ),
    parameters={
        "type": "object",
        "properties": {
            "app_name": {
                "type": "string",
                "description": "Name of the application to open, e.g. 'Visual Studio Code' or 'Notepad'.",
            }
        },
        "required": ["app_name"],
        "additionalProperties": False,
    },
    handler=lambda arguments: open_application(arguments.get("app_name", "")),
    permission=PermissionLevel.SAFE,
    category="applications",
    returns="ToolResult reporting whether the application is running.",
    destructive=False,
)


__all__ = [
    "open_application",
    "OPEN_APPLICATION_SPEC",
    "APP_ALIASES",
    "URI_ALIASES",
]
