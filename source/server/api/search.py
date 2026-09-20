from pathlib import Path
from fastapi import APIRouter
from server.config import DRIVE_DIR
from server.security.auth import require_user
from server.services.file_service import user_root

router=APIRouter(prefix="/api/search")

@router.get("")
def search(q:str="",extension:str="",kind:str="",request=None):
    q=q.lower().strip(); extension=extension.lower().lstrip("."); out=[]
    u=require_user(request); root=DRIVE_DIR if u["public"] else user_root(u["username"])
    kinds={"video":{".mp4",".mkv",".webm",".mov"},"audio":{".mp3",".wav",".ogg",".m4a"},"image":{".jpg",".jpeg",".png",".gif",".webp"},"text":{".txt",".md",".json",".csv",".py",".html",".css",".js"}}
    for p in root.rglob("*"):
        if not p.is_file(): continue
        rel=str(p.relative_to(root)).replace("\\","/")
        if rel.startswith("Corbeille/"): continue
        if q and q not in p.name.lower(): continue
        if extension and p.suffix.lower().lstrip(".")!=extension: continue
        if kind and p.suffix.lower() not in kinds.get(kind,set()): continue
        out.append({"name":p.name,"path":rel,"size":p.stat().st_size,"is_dir":False,"extension":p.suffix.lower()})
        if len(out)>=200: break
    return out
