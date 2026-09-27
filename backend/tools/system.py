import platform
import psutil
import shutil
import subprocess
from typing import Dict, Any


def get_hardware_info() -> Dict[str, Any]:
    """
    Detects local CPU, RAM, and GPU hardware to configure local inference without cloud dependencies.
    """
    info: Dict[str, Any] = {
        "os": f"{platform.system()} {platform.release()} ({platform.version()})",
        "processor": platform.processor() or platform.machine(),
        "cpu_count_logical": psutil.cpu_count(logical=True),
        "cpu_count_physical": psutil.cpu_count(logical=False),
        "cpu_percent": psutil.cpu_percent(interval=None),
        "ram_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
        "ram_available_gb": round(psutil.virtual_memory().available / (1024**3), 2),
        "ram_percent": psutil.virtual_memory().percent,
        "gpu_available": False,
        "gpu_name": None,
        "gpu_vram_gb": None,
        "cuda_available": False,
    }

    # Detect NVIDIA GPU via nvidia-smi if installed
    nvidia_smi = shutil.which("nvidia-smi")
    if nvidia_smi:
        try:
            cmd = [
                nvidia_smi,
                "--query-gpu=gpu_name,memory.total",
                "--format=csv,noheader,nounits",
            ]
            output = subprocess.check_output(cmd, encoding="utf-8", timeout=2).strip()
            if output:
                lines = output.splitlines()
                gpu_info = lines[0].split(",")
                info["gpu_available"] = True
                info["cuda_available"] = True
                info["gpu_name"] = gpu_info[0].strip()
                if len(gpu_info) > 1:
                    info["gpu_vram_gb"] = round(float(gpu_info[1].strip()) / 1024.0, 2)
        except Exception:
            pass

    return info
