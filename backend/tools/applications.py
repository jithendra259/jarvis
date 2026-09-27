import subprocess
import shutil
from typing import Dict, Any

APP_ALIASES = {
    "vscode": "code",
    "vs code": "code",
    "visual studio code": "code",
    "notepad": "notepad.exe",
    "calc": "calc.exe",
    "calculator": "calc.exe",
    "explorer": "explorer.exe",
    "file explorer": "explorer.exe",
    "files": "explorer.exe",
    "terminal": "wt.exe",
    "windows terminal": "wt.exe",
    "powershell": "powershell.exe",
    "cmd": "cmd.exe",
    "chrome": "chrome.exe",
    "browser": "chrome.exe",
    "edge": "msedge.exe",
}

def open_application(app_name: str) -> Dict[str, Any]:
    """Open an application on Windows by name or alias."""
    name_clean = app_name.strip().lower()
    target_cmd = APP_ALIASES.get(name_clean, name_clean)

    try:
        # Try launching via start command
        subprocess.Popen(f'start "" "{target_cmd}"', shell=True)
        return {
            "success": True,
            "message": f"Successfully launched {app_name}.",
            "target": target_cmd,
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to launch {app_name}: {str(e)}",
            "target": target_cmd,
        }

OPEN_APP_TOOL_SPEC = {
    "type": "function",
    "function": {
        "name": "open_application",
        "description": "Opens an installed Windows application such as VS Code, Notepad, Calculator, Chrome, Explorer, or Terminal.",
        "parameters": {
            "type": "object",
            "properties": {
                "app_name": {
                    "type": "string",
                    "description": "The common name of the application to open, e.g., 'VS Code', 'Notepad', 'Calculator', 'Chrome'.",
                }
            },
            "required": ["app_name"],
        },
    },
}
