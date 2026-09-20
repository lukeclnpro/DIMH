from fastapi import APIRouter, Request, Response
from pydantic import BaseModel
from server.security.auth import create_user, login_user, create_public_session, user_from_request

router = APIRouter(prefix='/api/auth')
class Credentials(BaseModel):
    username: str; password: str

@router.get('/me')
def me(request: Request): return user_from_request(request)

@router.post('/login')
def login(data: Credentials, response: Response):
    out = login_user(data.username, data.password); response.set_cookie('hd_session', out['token'], httponly=True, samesite='lax'); return {'username': out['username']}

@router.post('/public')
def public_login(response: Response):
    out = create_public_session()
    response.set_cookie('hd_session', out['token'], httponly=True, samesite='lax')
    return {'username': out['username'], 'public': True}

@router.post('/register')
def register(data: Credentials, response: Response):
    out = create_user(data.username, data.password); response.set_cookie('hd_session', out['token'], httponly=True, samesite='lax'); return {'username': out['username']}

@router.post('/logout')
def logout(response: Response): response.delete_cookie('hd_session'); return {'ok': True}
