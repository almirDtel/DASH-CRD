from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login import LoginManager
from fastapi_login.exceptions import InvalidCredentialsException
import json
from passlib.context import CryptContext

SECRET = "sua_chave_secreta_jwt"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()
manager = LoginManager(SECRET, token_url='/login')

with open("users.json") as f:
    USERS = json.load(f)["usernames"]

@manager.user_loader()
def load_user(username: str):
    return USERS.get(username)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

@app.post('/login')
def login(data: OAuth2PasswordRequestForm = Depends()):
    username = data.username
    password = data.password

    user = USERS.get(username)
    if not user or not verify_password(password, user.get("password")):
        raise InvalidCredentialsException

    access_token = manager.create_access_token(data={'sub': username})
    return {'access_token': access_token, 'token_type': 'bearer'}
