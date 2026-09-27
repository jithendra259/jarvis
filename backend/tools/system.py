"""System information and hardware detection.

Used by `/api/system/status` and to choose local inference settings (GPU vs
CPU). Detection is read-only and never requires administrator rights; fields
that cannot be determined are reported as null instead of guessed.
"""

from __future__ import annotations

import platform
import shutil
import subprocess
from typing import Any, Dict, List, Optional

from logger.logger import logger

try:
    import psutil
except ImportError:  # pragma: no cover
    psutil = None  # type: ignore[assignment]


def _nvidia_gpus() -> List[Dict[str, Any]]:
    executable = shutil.which("nvidia-smi")
    if not executable:
        return []
    try:
        output = subprocess.check_output(
            [
                executable,
                "--query-gpu=name,memory.total,driver_version",
                "--format=csv,noheader,nounits",
            ],
            encoding="utf-8",
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        logger.debug("nvidia-smi probe failed: %s", exc)
        return []

    gpus: List[Dict[str, Any]] = []
    for line in output.strip().splitlines():
        parts = [part.strip() for part in line.split(",")]
        if len(parts) < 2:
            continue
        try:
            vram_gb: Optional[float] = round(float(parts[1]) / 1024.0, 2)
        except ValueError:
            vram_gb = None
        gpus.append(
            {
                "name": parts[0],
                "vram_gb": vram_gb,
                "driver_version": parts[2] if len(parts) > 2 else None,
            }
        )
    return gpus


def _cpu_name() -> Optional[str]:
    if platform.system() == "Windows":
        try:
            import winreg

            key_path = r"HARDWARE\DESCRIPTION\System\CentralProcessor\0"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                value, _ = winreg.QueryValueEx(key, "ProcessorNameString")
                return str(value).strip()
        except (ImportError, OSError) as exc:  # pragma: no cover - Windows only
            logger.debug("CPU name lookup failed: %s", exc)
    return platform.processor() or platform.machine() or None


def get_hardware_info() -> Dict[str, Any]:
    """Detect CPU, RAM and GPU to configure local inference."""
    gpus = _nvidia_gpus()

    info: Dict[str, Any] = {
        "platform": platform.system(),
        "os": f"{platform.system()} {platform.release()} ({platform.version()})",
        "machine": platform.machine(),
        "python": platform.python_version(),
        "cpu": _cpu_name(),
        "cpu_count_logical": psutil.cpu_count(logical=True) if psutil else None,
        "cpu_count_physical": psutil.cpu_count(logical=False) if psutil else None,
        "cpu_percent": psutil.cpu_percent(interval=None) if psutil else None,
        "ram_total_gb": round(psutil.virtual_memory().total / (1024**3), 2) if psutil else None,
        "ram_available_gb": round(psutil.virtual_memory().available / (1024**3), 2) if psutil else None,
        "ram_percent": psutil.virtual_memory().percent if psutil else None,
        "gpu_available": bool(gpus),
        "gpu_count": len(gpus),
        "gpus": gpus,
        "gpu_name": gpus[0]["name"] if gpus else None,
        "gpu_vram_gb": gpus[0]["vram_gb"] if gpus else None,
        "cuda_available": bool(gpus),
    }

    if not gpus:
        try:
            import torch  # type: ignore

            info["torch_cuda_available"] = bool(torch.cuda.is_available())
        except Exception:
            info["torch_cuda_available"] = False

    info["recommended_inference"] = "gpu" if info["gpu_available"] else "cpu"
    return info


def get_service_status() -> Dict[str, Any]:
    """Process/agent level status used by the GUI status bar."""
    info: Dict[str, Any] = {"process_count": None, "load_percent": None}
    if psutil is None:
        return info
    info["process_count"] = len(psutil.pids())
    try:
        info["load_percent"] = round(psutil.cpu_percent(interval=0.1), 1)
    except Exception:  # pragma: no cover
        pass
    return info


__all__ = ["get_hardware_info", "get_service_status"]
