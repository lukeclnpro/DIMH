import os, time, tempfile, socket, psutil, subprocess
from pathlib import Path
from server.config import BASE_DIR, DRIVE_DIR

BOOT = time.time()

def stats():
    disk = psutil.disk_usage("/")
    drive = psutil.disk_usage(str(DRIVE_DIR))
    vm = psutil.virtual_memory()
    return {
        "cpu": psutil.cpu_percent(interval=0.15),
        "ram_percent": vm.percent,
        "ram_used": vm.used,
        "ram_total": vm.total,
        "disk_percent": disk.percent,
        "disk_used": disk.used,
        "disk_total": disk.total,
        "drive_percent": drive.percent,
        "drive_used": drive.used,
        "drive_total": drive.total,
        "uptime": int(time.time() - BOOT),
        "hostname": os.uname().nodename if hasattr(os, "uname") else os.getenv("COMPUTERNAME", "PC"),
    }

def disk_write_benchmark(size_mb: int = 64):
    size_mb = max(8, min(int(size_mb), 256))
    block = os.urandom(1024 * 1024)
    fd, name = tempfile.mkstemp(prefix=".homedrive-benchmark-", dir=str(DRIVE_DIR))
    start = time.perf_counter()
    try:
        with os.fdopen(fd, "wb", buffering=0) as f:
            for _ in range(size_mb):
                f.write(block)
            f.flush()
            os.fsync(f.fileno())
        elapsed = max(time.perf_counter() - start, 0.000001)
        return {"size_mb": size_mb, "write_mbps": round(size_mb / elapsed, 2), "elapsed": round(elapsed, 3)}
    finally:
        try: os.remove(name)
        except OSError: pass


def update_from_repository():
    script = BASE_DIR / "scripts" / "update.sh"
    result = subprocess.run(
        [str(script)],
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
        timeout=600,
        check=False,
    )
    output = (result.stdout + "\n" + result.stderr).strip()
    if result.returncode:
        raise RuntimeError(output or "La mise à jour a échoué.")
    return {"ok": True, "message": output or "HomeDrive mis à jour."}
