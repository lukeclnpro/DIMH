from pathlib import Path
import shutil
from fastapi import HTTPException, UploadFile
from server.config import DRIVE_DIR

def safe_path(relative: str = "") -> Path:
    relative = relative.replace("\\", "/").lstrip("/")
    target = (DRIVE_DIR / relative).resolve()
    try: target.relative_to(DRIVE_DIR)
    except ValueError: raise HTTPException(400, "Chemin invalide")
    return target

def user_root(username: str) -> Path:
    root = (DRIVE_DIR / username).resolve()
    try: root.relative_to(DRIVE_DIR)
    except ValueError: raise HTTPException(400, "Espace utilisateur invalide")
    root.mkdir(parents=True, exist_ok=True)
    return root

def safe_user_path(relative: str = "", username: str = "") -> Path:
    root = user_root(username)
    relative = relative.replace("\\", "/").lstrip("/")
    target = (root / relative).resolve()
    try: target.relative_to(root)
    except ValueError: raise HTTPException(400, "Chemin invalide")
    return target

def item_info(path: Path):
    st=path.stat()
    return {"name":path.name,"path":str(path.relative_to(DRIVE_DIR)),"is_dir":path.is_dir(),"size":0 if path.is_dir() else st.st_size,"modified":st.st_mtime,"extension":path.suffix.lower()}

def user_item_info(path: Path, root: Path):
    st=path.stat()
    return {"name":path.name,"path":str(path.relative_to(root)).replace("\\","/"),"is_dir":path.is_dir(),"size":0 if path.is_dir() else st.st_size,"modified":st.st_mtime,"extension":path.suffix.lower()}

def list_user_dir(relative="", username=""):
    root=user_root(username); path=safe_user_path(relative,username)
    if not path.exists() or not path.is_dir(): raise HTTPException(404,"Dossier introuvable")
    return sorted([user_item_info(p,root) for p in path.iterdir()],key=lambda x:(not x["is_dir"],x["name"].lower()))

def list_dir(relative=""):
    path=safe_path(relative)
    if not path.exists() or not path.is_dir(): raise HTTPException(404,"Dossier introuvable")
    return sorted([item_info(p) for p in path.iterdir()],key=lambda x:(not x["is_dir"],x["name"].lower()))

def create_user_folder(relative,name,username):
    if not name or "/" in name or "\\" in name: raise HTTPException(400,"Nom de dossier invalide")
    target=safe_user_path(relative,username)/name; target.mkdir()
    return user_item_info(target,user_root(username))

def create_user_text(relative,name,content,username):
    if not name or "/" in name or "\\" in name: raise HTTPException(400,"Nom de fichier invalide")
    target=safe_user_path(relative,username)/name
    if target.exists(): raise HTTPException(409,"Le fichier existe déjà")
    target.write_text(content,encoding="utf-8")
    return user_item_info(target,user_root(username))

def unique_sibling_name(dst: Path) -> Path:
    """Retourne un chemin frère disponible du type 'nom (1).ext', 'nom (2).ext', ..."""
    stem,suffix=dst.stem,dst.suffix; i=1
    while dst.exists():
        dst=dst.parent/f"{stem} ({i}){suffix}"; i+=1
    return dst

def resolve_conflict(dst: Path, on_conflict: str) -> Path:
    """on_conflict: 'abort' (défaut, lève 409), 'replace' (écrase), 'rename' (garde les deux)."""
    if not dst.exists(): return dst
    if on_conflict=="replace":
        if dst.is_dir(): shutil.rmtree(dst)
        else: dst.unlink()
        return dst
    if on_conflict=="rename": return unique_sibling_name(dst)
    raise HTTPException(409,"Le fichier existe déjà")

def user_save_upload(relative,upload,username,on_conflict="abort"):
    folder=safe_user_path(relative,username)
    if not folder.is_dir(): raise HTTPException(404,"Dossier introuvable")
    filename=Path(upload.filename or "fichier").name; dst=folder/filename
    return resolve_conflict(dst,on_conflict)

def user_path_exists(relative,name,username) -> bool:
    folder=safe_user_path(relative,username)
    if not folder.is_dir(): raise HTTPException(404,"Dossier introuvable")
    return (folder/Path(name or "").name).exists()

def user_trash_one(relative,username):
    root=user_root(username); src=safe_user_path(relative,username)
    if not src.exists(): raise HTTPException(404,"Élément introuvable")
    trash_dir=safe_user_path("Corbeille",username); trash_dir.mkdir(exist_ok=True)
    dst=trash_dir/src.name; i=1
    while dst.exists(): dst=trash_dir/f"{src.stem}_{i}{src.suffix}"; i+=1
    shutil.move(str(src),str(dst)); return user_item_info(dst,root)

def user_move_one(relative,destination,username,on_conflict="abort"):
    root=user_root(username)
    src=safe_user_path(relative,username); dst_dir=safe_user_path(destination,username)
    if not src.exists(): raise HTTPException(404,f"Élément introuvable : {relative}")
    if not dst_dir.is_dir(): raise HTTPException(404,"Dossier de destination introuvable")
    if src==dst_dir or (src.is_dir() and dst_dir.is_relative_to(src)): raise HTTPException(400,"Destination invalide")
    if src.parent==dst_dir: raise HTTPException(409,"L'élément est déjà dans ce dossier")
    dst=resolve_conflict(dst_dir/src.name,on_conflict)
    shutil.move(str(src),str(dst)); return user_item_info(dst,root)

def user_copy_one(relative,destination,username,on_conflict="abort"):
    root=user_root(username)
    src=safe_user_path(relative,username); dst_dir=safe_user_path(destination,username)
    if not src.exists(): raise HTTPException(404,f"Élément introuvable : {relative}")
    if not dst_dir.is_dir(): raise HTTPException(404,"Dossier de destination introuvable")
    if src.is_dir() and dst_dir.is_relative_to(src): raise HTTPException(400,"Destination invalide")
    dst=resolve_conflict(dst_dir/src.name,on_conflict)
    (shutil.copytree(src,dst) if src.is_dir() else shutil.copy2(src,dst))
    return user_item_info(dst,root)

def create_folder(relative,name):
    if not name or "/" in name or "\\" in name: raise HTTPException(400,"Nom de dossier invalide")
    target=safe_path(relative)/name; target.mkdir(); return item_info(target)

def create_text(relative,name,content=""):
    if not name or "/" in name or "\\" in name: raise HTTPException(400,"Nom de fichier invalide")
    target=safe_path(relative)/name
    if target.exists(): raise HTTPException(409,"Le fichier existe déjà")
    target.write_text(content,encoding="utf-8"); return item_info(target)

async def save_upload(relative,upload):
    folder=safe_path(relative)
    if not folder.is_dir(): raise HTTPException(404,"Dossier introuvable")
    filename=Path(upload.filename or "fichier").name; dst=folder/filename
    if dst.exists(): raise HTTPException(409,"Le fichier existe déjà")
    with dst.open("wb") as f:
        while chunk:=await upload.read(1024*1024): f.write(chunk)
    return item_info(dst)

def rename(relative,new_name):
    src=safe_path(relative)
    if not src.exists() or not new_name or "/" in new_name or "\\" in new_name: raise HTTPException(400,"Opération invalide")
    dst=src.parent/new_name
    if dst.exists(): raise HTTPException(409,"La destination existe déjà")
    src.rename(dst); return item_info(dst)

def move(relative,destination):
    src=safe_path(relative); dst_dir=safe_path(destination)
    if not src.exists() or not dst_dir.is_dir(): raise HTTPException(404,"Élément ou destination introuvable")
    dst=dst_dir/src.name
    if dst.exists(): raise HTTPException(409,"La destination existe déjà")
    shutil.move(str(src),str(dst)); return item_info(dst)

def copy(relative,destination):
    src=safe_path(relative); dst_dir=safe_path(destination); dst=dst_dir/src.name
    if dst.exists(): raise HTTPException(409,"La destination existe déjà")
    shutil.copytree(src,dst) if src.is_dir() else shutil.copy2(src,dst); return item_info(dst)

def trash(relative):
    src=safe_path(relative)
    if not src.exists(): raise HTTPException(404,"Élément introuvable")
    dst_dir=DRIVE_DIR/"Corbeille"; dst_dir.mkdir(exist_ok=True); dst=dst_dir/src.name; i=1
    while dst.exists(): dst=dst_dir/f"{src.stem}_{i}{src.suffix}"; i+=1
    shutil.move(str(src),str(dst)); return item_info(dst)
