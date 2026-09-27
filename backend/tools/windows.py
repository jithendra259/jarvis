"""Windows system inspection and computer control tools.

Provides:
  * get_system_information: CPU, RAM, GPU, OS, disk space and battery
  * get_running_processes: list active processes sorted by memory or filtered by name
  * get_clipboard: read plain text from the Windows clipboard
  * set_clipboard: write text to the Windows clipboard
  * open_browser: open a URL or search query in the user's default browser
"""

from __future__ import annotations

import os
import platform
import subprocess
import time
import webbrowser
from typing import Any, Dict, List, Optional

from logger.logger import logger
from security.permissions import PermissionLevel
from tools.base import ToolResult, ToolSpec
from tools.system import get_hardware_info

try:
    import psutil
except ImportError:
    psutil = None


def get_system_information() -> ToolResult:
    """Retrieve full hardware, platform and resource telemetry."""
    hw = get_hardware_info()
    data: Dict[str, Any] = dict(hw)

    if psutil:
        try:
            disk = psutil.disk_usage(os.path.splitdrive(os.getcwd())[0] or "C:")
            data["disk_total_gb"] = round(disk.total / (1024**3), 2)
            data["disk_free_gb"] = round(disk.free / (1024**3), 2)
            data["disk_percent"] = disk.percent
        except Exception as exc:
            logger.debug("disk check failed: %s", exc)

        try:
            battery = psutil.sensors_battery()
            if battery:
                data["battery_percent"] = round(battery.percent, 1)
                data["battery_plugged"] = battery.power_plugged
        except Exception:
            pass

    summary = (
        f"OS: {data.get('os')}. CPU: {data.get('cpu')} ({data.get('cpu_count_logical')} logical cores, "
        f"{data.get('cpu_percent')}% load). RAM: {data.get('ram_available_gb')} GB available of {data.get('ram_total_gb')} GB. "
        f"GPU: {data.get('gpu_name') or 'Integrated / None'}."
    )
    return ToolResult(tool="get_system_information", success=True, message=summary, data=data)


def get_running_processes(
    filter_name: Optional[str] = None,
    limit: int = 15,
) -> ToolResult:
    """List running processes on the system."""
    if psutil is None:
        return ToolResult.failure("get_running_processes", "psutil is required to list processes.")

    limit = max(1, min(limit, 50))
    procs: List[Dict[str, Any]] = []

    for proc in psutil.process_iter(["pid", "name", "memory_info", "cpu_percent"]):
        try:
            info = proc.info
            name = info.get("name") or ""
            if filter_name and filter_name.lower() not in name.lower():
                continue
            mem_mb = 0.0
            if info.get("memory_info"):
                mem_mb = round(info["memory_info"].rss / (1024 * 1024), 1)
            procs.append({
                "pid": info.get("pid"),
                "name": name,
                "memory_mb": mem_mb,
                "cpu_percent": info.get("cpu_percent") or 0.0,
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    procs.sort(key=lambda p: p["memory_mb"], reverse=True)
    selected = procs[:limit]

    message = f"Found {len(procs)} matching processes (showing top {len(selected)})."
    return ToolResult(
        tool="get_running_processes",
        success=True,
        message=message,
        data={"processes": selected, "total_matched": len(procs)},
    )


def get_clipboard() -> ToolResult:
    """Read plain text from the Windows clipboard."""
    try:
        proc = subprocess.run(
            ["powershell", "-NoProfile", "-Command", "Get-Clipboard"],
            capture_output=True,
            text=True,
            timeout=5,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        content = proc.stdout.rstrip("\r\n")
        return ToolResult(
            tool="get_clipboard",
            success=True,
            message="Read clipboard successfully." if content else "Clipboard is empty.",
            data={"content": content, "length": len(content)},
        )
    except Exception as exc:
        return ToolResult.failure("get_clipboard", f"Failed to read clipboard: {exc}")


def set_clipboard(text: str) -> ToolResult:
    """Copy text to the Windows clipboard."""
    try:
        proc = subprocess.Popen(
            ["powershell", "-NoProfile", "-Command", "$input | Set-Clipboard"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        _, stderr = proc.communicate(input=text, timeout=5)
        if proc.returncode != 0:
            return ToolResult.failure("set_clipboard", f"Failed to set clipboard: {stderr}")
        return ToolResult(
            tool="set_clipboard",
            success=True,
            message=f"Copied {len(text)} characters to the clipboard.",
            data={"length": len(text)},
        )
    except Exception as exc:
        return ToolResult.failure("set_clipboard", f"Failed to copy to clipboard: {exc}")


def open_browser(url: str) -> ToolResult:
    """Open a URL in the user's default browser."""
    if not url or not url.strip():
        return ToolResult.failure("open_browser", "URL cannot be empty.")
    target = url.strip()
    if not target.startswith(("http://", "https://", "file://")):
        if "." in target and not target.startswith("www."):
            target = f"https://{target}"
        else:
            target = f"https://www.google.com/search?q={target.replace(' ', '+')}"

    try:
        opened = webbrowser.open(target)
        return ToolResult(
            tool="open_browser",
            success=opened,
            message=f"Opened {target} in default web browser.",
            data={"url": target},
        )
    except Exception as exc:
        return ToolResult.failure("open_browser", f"Failed to open browser: {exc}")


# ---------------------------------------------------------------------------
# Tool Specs
# ---------------------------------------------------------------------------
GET_SYSTEM_INFORMATION_SPEC = ToolSpec(
    name="get_system_information",
    description="Retrieve Windows system information: CPU model and usage, available RAM, GPU, OS version and disk space.",
    parameters={"type": "object", "properties": {}, "additionalProperties": False},
    handler=lambda _args: get_system_information(),
    permission=PermissionLevel.SAFE,
    category="system",
    returns="ToolResult with system and hardware telemetry.",
)

GET_RUNNING_PROCESSES_SPEC = ToolSpec(
    name="get_running_processes",
    description="List active processes running on Windows, sorted by memory usage or filtered by application name.",
    parameters={
        "type": "object",
        "properties": {
            "filter_name": {
                "type": "string",
                "description": "Optional name filter (e.g. 'chrome', 'python', 'code').",
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of processes to return (default 15).",
            },
        },
        "additionalProperties": False,
    },
    handler=lambda args: get_running_processes(
        filter_name=args.get("filter_name"),
        limit=int(args.get("limit", 15)),
    ),
    permission=PermissionLevel.SAFE,
    category="system",
    returns="ToolResult with process list.",
)

GET_CLIPBOARD_SPEC = ToolSpec(
    name="get_clipboard",
    description="Read the current text content from the Windows clipboard.",
    parameters={"type": "object", "properties": {}, "additionalProperties": False},
    handler=lambda _args: get_clipboard(),
    permission=PermissionLevel.SAFE,
    category="system",
    returns="ToolResult with clipboard text.",
)

SET_CLIPBOARD_SPEC = ToolSpec(
    name="set_clipboard",
    description="Copy text to the Windows clipboard.",
    parameters={
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": "Text to place on the clipboard.",
            }
        },
        "required": ["text"],
        "additionalProperties": False,
    },
    handler=lambda args: set_clipboard(str(args.get("text", ""))),
    permission=PermissionLevel.SAFE,
    category="system",
    returns="ToolResult confirming clipboard update.",
)

OPEN_BROWSER_SPEC = ToolSpec(
    name="open_browser",
    description="Open a website URL or web search in the user's default web browser.",
    parameters={
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "URL to navigate to (e.g. 'https://github.com') or search query.",
            }
        },
        "required": ["url"],
        "additionalProperties": False,
    },
    handler=lambda args: open_browser(str(args.get("url", ""))),
    permission=PermissionLevel.SAFE,
    category="browser",
    returns="ToolResult confirming browser launch.",
)
