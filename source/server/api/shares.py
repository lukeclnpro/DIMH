import secrets, time, sqlite3
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from server.services.file_service import safe_path, safe_user_path
from server.security.auth import user_from_request, _db

router = APIRouter(prefix='/api/shares')
SHARES = {}
class UserShare(BaseModel):
    username: str; permission: str = 'read'

@router.get('/users')
def available_users(request: Request):
    """Liste les comptes utilisateurs disponibles pour un partage."""
    user=user_from_request(request)
    if user['public']: raise HTTPException(401,'Connexion requise')
    db=_db()
    rows=db.execute('SELECT username FROM users ORDER BY username COLLATE NOCASE').fetchall()
    db.close()
    return [{'username':r['username']} for r in rows if r['username'] != user['username']]

@router.post('/public')
def create_public_share(path: str, expires: int = 0, request: Request = None):
    user=user_from_request(request)
    if user['public']: raise HTTPException(401,'Connexion requise')
    p=safe_user_path(path, user['username'])
    if not p.is_file(): raise HTTPException(404,'Fichier introuvable')
    token=secrets.token_urlsafe(10); SHARES[token]=(str(p), time.time()+expires if expires else 0)
    return {'token':token,'expires':expires}

@router.post('/user')
def share_user(path: str, data: UserShare, request: Request):
    user=user_from_request(request)
    if user['public']: raise HTTPException(401,'Connectez-vous pour partager avec un utilisateur')
    p=safe_user_path(path, user['username'])
    if not p.is_file(): raise HTTPException(404,'Fichier introuvable')
    db=_db(); target=db.execute('SELECT id,username FROM users WHERE username=?',(data.username.strip().lower(),)).fetchone()
    if not target: db.close(); raise HTTPException(404,'Utilisateur introuvable')
    db.execute('CREATE TABLE IF NOT EXISTS user_shares (id INTEGER PRIMARY KEY AUTOINCREMENT, token TEXT UNIQUE, path TEXT, owner_id INTEGER, target_id INTEGER, permission TEXT, created_at REAL)')
    token=secrets.token_urlsafe(16)
    db.execute('INSERT INTO user_shares(token,path,owner_id,target_id,permission,created_at) VALUES(?,?,?,?,?,strftime("%s","now"))',(token,str(p),user['id'],target['id'],data.permission)); db.commit(); db.close()
    return {'ok':True,'user':target['username'],'permission':data.permission}

@router.get('/mine')
def my_shares(request: Request):
    user=user_from_request(request)
    if user['public']: return []
    db=_db(); db.execute('CREATE TABLE IF NOT EXISTS user_shares (id INTEGER PRIMARY KEY AUTOINCREMENT, token TEXT UNIQUE, path TEXT, owner_id INTEGER, target_id INTEGER, permission TEXT, created_at REAL)')
    rows=db.execute('SELECT s.token,s.path,s.permission,u.username FROM user_shares s JOIN users u ON u.id=s.owner_id WHERE s.target_id=?',(user['id'],)).fetchall(); db.close()
    return [{'path':r['path'],'token':r['token'],'permission':r['permission'],'owner':r['username']} for r in rows]

@router.get('/{token}')
def get_share(token: str):
    data=SHARES.get(token)
    if not data: raise HTTPException(404,'Partage introuvable')
    path,expiry=data
    if expiry and time.time()>expiry: SHARES.pop(token,None); raise HTTPException(410,'Partage expiré')
    return FileResponse(path)


def user_shared_file(token, request: Request):
    user=user_from_request(request)
    if user['public']: raise HTTPException(401,'Connexion requise')
    db=_db(); row=db.execute('SELECT path,permission FROM user_shares WHERE token=? AND target_id=?',(token,user['id'])).fetchone(); db.close()
    if not row: raise HTTPException(404,'Partage introuvable')
    return row['path'], row['permission']

@router.get('/user/{token}')
def get_user_share(token: str, request: Request):
    path, _=user_shared_file(token, request); return FileResponse(path)
