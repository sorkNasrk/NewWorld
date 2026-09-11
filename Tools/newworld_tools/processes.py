from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Sequence


def start_detached(args: Sequence[str | Path], cwd: Path, visible: bool = False) -> subprocess.Popen:
    popen_args = [str(arg) for arg in args]
    kwargs: dict[str, object] = {
        "cwd": str(cwd),
        "stdin": subprocess.DEVNULL,
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
    }

    if os.name == "nt":
        creationflags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
        if not visible:
            creationflags |= getattr(subprocess, "CREATE_NO_WINDOW", 0)
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = 0
            kwargs["startupinfo"] = startupinfo
        kwargs["creationflags"] = creationflags

    return subprocess.Popen(popen_args, **kwargs)

