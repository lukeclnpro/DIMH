import subprocess

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import Response
from server.security.auth import require_user
from server.services.system_service import stats, disk_write_benchmark, update_from_repository

router = APIRouter(prefix="/api/system")

@router.get("/stats")
def system_stats():
    return stats()

@router.post("/disk-benchmark")
def disk_benchmark(size_mb: int = Query(64, ge=8, le=256)):
    return disk_write_benchmark(size_mb)

@router.get("/download-test")
def download_test(size: int = Query(16 * 1024 * 1024, ge=1024, le=64 * 1024 * 1024)):
    # Flux binaire généré en mémoire pour mesurer le débit navigateur <-> serveur.
    block = b"\0" * (1024 * 1024)
    chunks = [block] * (size // len(block))
    remainder = size % len(block)
    body = b"".join(chunks) + (b"\0" * remainder)
    return Response(content=body, media_type="application/octet-stream", headers={"Cache-Control":"no-store"})


@router.post("/update")
def update_service(request: Request):
    user = require_user(request)
    if user["public"]:
        raise HTTPException(status_code=403, detail="Le compte public ne peut pas mettre à jour HomeDrive.")
    try:
        return update_from_repository()
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="La mise à jour a dépassé le délai autorisé.")
    except (OSError, RuntimeError) as error:
        raise HTTPException(status_code=500, detail=str(error))
