from pathlib import Path
import shutil
from fastapi import APIRouter, UploadFile, File, Request, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from server.security.auth import require_user
from server.api.shares import user_shared_file
from server.services.file_service import *
from server.config import TEXT_EXTENSIONS, DRIVE_DIR

router=APIRouter(prefix="/api/files")

class PathsBody(BaseModel):
    paths: list[str]

def write_user(request):
    u=require_user(request)
    if u["public"]: raise HTTPException(403,"Le compte public est en lecture seule. Connectez-vous pour modifier le Drive.")
    return u

@router.get("")
def files(path:str="",request:Request=None):
    u=require_user(request)
    if u["public"]: return list_dir(path)
    if path=="Partages":
        return [] if u["public"] else _received_shares(u["id"])
    return list_user_dir(path,u["username"])

def _received_shares(user_id):
    from server.security.auth import _db
    db=_db()
    db.execute("CREATE TABLE IF NOT EXISTS user_shares (id INTEGER PRIMARY KEY AUTOINCREMENT, token TEXT UNIQUE, path TEXT, owner_id INTEGER, target_id INTEGER, permission TEXT, created_at REAL)")
    rows=db.execute("SELECT s.token,s.path,s.permission,u.username FROM user_shares s JOIN users u ON u.id=s.owner_id WHERE s.target_id=?",(user_id,)).fetchall(); db.close()
    return [{"name":Path(r["path"]).name+" — partagé par "+r["username"],"path":"__share__/"+r["token"],"is_dir":False,"size":Path(r["path"]).stat().st_size,"modified":Path(r["path"]).stat().st_mtime,"extension":Path(r["path"]).suffix.lower(),"shared":True,"permission":r["permission"]} for r in rows if Path(r["path"]).exists()]

@router.post("/folder")
def folder(path:str,name:str,request:Request=None):
    u=write_user(request); return create_user_folder(path,name,u["username"])

@router.post("/text")
def text_file(path:str,name:str,content:str="",request:Request=None):
    u=write_user(request); return create_user_text(path,name,content,u["username"])

@router.get("/exists")
def exists(path:str="",name:str="",request:Request=None):
    u=require_user(request)
    if u["public"]: return {"exists":False}
    return {"exists":user_path_exists(path,name,u["username"])}

@router.post("/upload")
async def upload(path:str="",on_conflict:str="abort",file:UploadFile=File(...),request:Request=None):
    u=write_user(request)
    if on_conflict not in ("abort","replace","rename"): on_conflict="abort"
    dst=user_save_upload(path,file,u["username"],on_conflict)
    with dst.open("wb") as f:
        while chunk:=await file.read(1024*1024): f.write(chunk)
    return user_item_info(dst,user_root(u["username"]))

@router.get("/download")
def download(path:str,request:Request=None):
    u=require_user(request)
    if path.startswith("__share__/"): p=Path(user_shared_file(path.split("/",1)[1],request)[0])
    else: p=safe_user_path(path,u["username"]) if not u["public"] else safe_path(path)
    if not p.is_file(): raise HTTPException(404,"Fichier introuvable")
    return FileResponse(p,filename=p.name)

@router.get("/raw")
def raw(path:str,request:Request=None):
    return download(path,request)

@router.get("/text")
def read_text(path:str,request:Request=None):
    u=require_user(request); p=safe_user_path(path,u["username"]) if not u["public"] else safe_path(path)
    if p.suffix.lower() not in TEXT_EXTENSIONS or not p.is_file(): raise HTTPException(400,"Fichier texte non pris en charge")
    return {"path":path,"content":p.read_text(encoding="utf-8",errors="replace")}

@router.put("/text")
def write_text(path:str,content:str,request:Request=None):
    u=write_user(request); p=safe_user_path(path,u["username"])
    if p.suffix.lower() not in TEXT_EXTENSIONS or not p.is_file(): raise HTTPException(400,"Fichier texte non pris en charge")
    p.write_text(content,encoding="utf-8"); return {"ok":True}

@router.post("/rename")
def rename_file(path:str,new_name:str,request:Request=None):
    u=write_user(request); p=safe_user_path(path,u["username"])
    if not p.exists() or not new_name or "/" in new_name or "\\" in new_name: raise HTTPException(400,"Opération invalide")
    dst=p.parent/new_name
    if dst.exists(): raise HTTPException(409,"La destination existe déjà")
    p.rename(dst); return user_item_info(dst,user_root(u["username"]))

@router.post("/move")
def move_files(destination:str,data:PathsBody,on_conflict:str="abort",request:Request=None):
    u=write_user(request)
    if on_conflict not in ("abort","replace","rename"): on_conflict="abort"
    results=[]
    for p in data.paths:
        try: results.append({"path":p,"ok":True,"item":user_move_one(p,destination,u["username"],on_conflict)})
        except HTTPException as e: results.append({"path":p,"ok":False,"error":e.detail})
    return results

@router.post("/copy")
def copy_files(destination:str,data:PathsBody,on_conflict:str="abort",request:Request=None):
    u=write_user(request)
    if on_conflict not in ("abort","replace","rename"): on_conflict="abort"
    results=[]
    for p in data.paths:
        try: results.append({"path":p,"ok":True,"item":user_copy_one(p,destination,u["username"],on_conflict)})
        except HTTPException as e: results.append({"path":p,"ok":False,"error":e.detail})
    return results

@router.post("/delete-batch")
def delete_batch(data:PathsBody,request:Request=None):
    u=write_user(request)
    results=[]
    for p in data.paths:
        try: results.append({"path":p,"ok":True,"item":user_trash_one(p,u["username"])})
        except HTTPException as e: results.append({"path":p,"ok":False,"error":e.detail})
    return results

@router.delete("")
def delete_file(path:str,request:Request=None):
    u=write_user(request); return user_trash_one(path,u["username"])
