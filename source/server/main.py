from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from server.config import DRIVE_DIR, USER_FOLDERS
from server.api import files, search, system, shares, auth, spreadsheets

app = FastAPI(title="HomeDrive", version="0.1.0")
DRIVE_DIR.mkdir(parents=True, exist_ok=True)

for name in ["Documents","Images","Musique","Videos","Applications","Archives","Partages","Corbeille"]:
    (DRIVE_DIR / name).mkdir(exist_ok=True)

app.include_router(files.router)
app.include_router(search.router)
app.include_router(system.router)
app.include_router(shares.router)
app.include_router(auth.router)
app.include_router(spreadsheets.router)

WEB = Path(__file__).resolve().parent.parent / "web"
app.mount("/", StaticFiles(directory=WEB, html=True), name="web")
