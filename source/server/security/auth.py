import hashlib, hmac, secrets, sqlite3
from pathlib import Path
from fastapi import Request, HTTPException
from server.config import AUTH_DB, DRIVE_DIR, USER_FOLDERS

PUBLIC_USERNAME = 'public'


def _db():
    AUTH_DB.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(AUTH_DB)
    c.row_factory = sqlite3.Row
    c.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, salt TEXT NOT NULL, created_at REAL NOT NULL)')
    c.execute('CREATE TABLE IF NOT EXISTS sessions (token TEXT PRIMARY KEY, user_id INTEGER, created_at REAL NOT NULL)')
    c.commit(); return c


def _hash(password, salt=None):
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 200_000).hex()
    return digest, salt


def ensure_public_user():
    """Crée le compte public réel, sans mot de passe utilisable pour une connexion classique."""
    db = _db()
    row = db.execute('SELECT id FROM users WHERE username=?', (PUBLIC_USERNAME,)).fetchone()
    if not row:
        # Empêche toute connexion classique par mot de passe au compte public.
        h, salt = _hash(secrets.token_urlsafe(48))
        db.execute('INSERT INTO users(username,password_hash,salt,created_at) VALUES(?,?,?,strftime("%s","now"))', (PUBLIC_USERNAME, h, salt))
        db.commit()
    row = db.execute('SELECT id FROM users WHERE username=?', (PUBLIC_USERNAME,)).fetchone()
    db.close()
    return row['id']


def ensure_user_drive(username):
    user_dir = DRIVE_DIR / username
    user_dir.mkdir(parents=True, exist_ok=True)
    for folder in USER_FOLDERS:
        src = DRIVE_DIR / folder
        dst = user_dir / folder
        dst.mkdir(parents=True, exist_ok=True)
        if src.exists() and src.is_dir():
            for child in src.rglob('*'):
                if child.is_dir():
                    (dst / child.relative_to(src)).mkdir(parents=True, exist_ok=True)
    return user_dir


def create_public_session():
    user_id = ensure_public_user()
    ensure_user_drive(PUBLIC_USERNAME)
    token = secrets.token_urlsafe(32)
    db = _db()
    db.execute('INSERT INTO sessions(token,user_id,created_at) VALUES(?,?,strftime("%s","now"))', (token, user_id))
    db.commit(); db.close()
    return {'token': token, 'username': PUBLIC_USERNAME, 'public': True}


def create_user(username, password):
    username = username.strip().lower()
    if username == PUBLIC_USERNAME:
        raise HTTPException(400, 'Le compte public est réservé.')
    if len(username) < 3 or len(password) < 6:
        raise HTTPException(400, 'Identifiant : 3 caractères minimum. Mot de passe : 6 caractères minimum.')
    db = _db(); h, salt = _hash(password)
    try:
        db.execute('INSERT INTO users(username,password_hash,salt,created_at) VALUES(?,?,?,strftime("%s","now"))', (username,h,salt)); db.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(409, 'Cet identifiant existe déjà')
    finally: db.close()
    ensure_user_drive(username)
    return login_user(username, password)


def login_user(username, password):
    username = username.strip().lower()
    if username == PUBLIC_USERNAME:
        raise HTTPException(401, 'Le compte public se connecte sans mot de passe.')
    db = _db(); row = db.execute('SELECT * FROM users WHERE username=?', (username,)).fetchone()
    if not row: db.close(); raise HTTPException(401, 'Identifiants incorrects')
    h, _ = _hash(password, row['salt'])
    if not hmac.compare_digest(h, row['password_hash']): db.close(); raise HTTPException(401, 'Identifiants incorrects')
    ensure_user_drive(row['username'])
    token = secrets.token_urlsafe(32)
    db.execute('INSERT INTO sessions(token,user_id,created_at) VALUES(?,?,strftime("%s","now"))', (token,row['id'])); db.commit(); db.close()
    return {'token': token, 'username': row['username'], 'public': False}


def user_from_request(request: Request):
    token = request.cookies.get('hd_session') or request.headers.get('X-HomeDrive-Session')
    if not token: return {'id': 0, 'username': 'public', 'public': True}
    db = _db(); row = db.execute('SELECT u.id,u.username FROM sessions s JOIN users u ON u.id=s.user_id WHERE s.token=?', (token,)).fetchone(); db.close()
    if not row: return {'id': 0, 'username': 'public', 'public': True}
    return {'id': row['id'], 'username': row['username'], 'public': row['username'] == PUBLIC_USERNAME}


def require_user(request: Request):
    return user_from_request(request)
