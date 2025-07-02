from fastapi import Depends, FastAPI, HTTPException, Request, status, Response
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import timedelta
from redis.asyncio import Redis
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from fastapi_csrf_protect import CsrfProtect
from fastapi_csrf_protect.exceptions import CsrfProtectError
from pydantic import BaseModel
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import pyotp
import qrcode
import io
from base64 import b64encode
import structlog

from . import crud, models, schemas
from .auth import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
)
from .database import engine, get_db
from .logging_config import setup_logging
from .utils import format_error
from .config import get_settings

log = structlog.get_logger()

models.Base.metadata.create_all(bind=engine)

setup_logging()

app = FastAPI(
    title="Web Template API",
    description="Simple authentication service built with FastAPI",
    version="0.1.0",
)

# CSRF Settings
class CsrfSettings(BaseModel):
    secret_key: str

@CsrfProtect.load_config
def get_csrf_config():
    return CsrfSettings(secret_key=get_settings().CSRF_SECRET_KEY)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


@app.on_event("startup")
async def startup():
    redis = Redis(host="redis", port=6379, db=0, encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(redis)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Return JSON error responses for unexpected exceptions."""
    log.exception("Unhandled exception", exc_info=exc)
    return JSONResponse(status_code=500, content=format_error("Internal server error"))

# CSRF Exception Handler
@app.exception_handler(CsrfProtectError)
def csrf_protect_exception_handler(request: Request, exc: CsrfProtectError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@app.post("/signup", response_model=schemas.UserOut)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db, user)


async def get_current_user_from_cookie(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    username: str = payload.get("sub")
    user = crud.get_user_by_username(db, username)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.get("/users/me", response_model=schemas.UserOut)
def read_users_me(
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    return current_user


@app.post("/refresh")
def refresh_token(request: Request, response: Response, db: Session = Depends(get_db), csrf_protect: CsrfProtect = Depends()):
    csrf_protect.validate_csrf(request)
    refresh_token_from_cookie = request.cookies.get("refresh_token")
    if not refresh_token_from_cookie:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    payload = decode_access_token(refresh_token_from_cookie)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    username: str = payload.get("sub")
    user = crud.get_user_by_username(db, username)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    access_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    new_access_token = create_access_token({"sub": username}, expires_delta=access_expires)
    new_refresh_token = create_refresh_token({"sub": username}, expires_delta=refresh_expires)

    csrf_protect.set_access_cookies(new_access_token, response)
    csrf_protect.set_refresh_cookies(new_refresh_token, response)
    response.set_cookie(key="access_token", value=new_access_token, httponly=True, expires=access_expires.total_seconds())
    response.set_cookie(key="refresh_token", value=new_refresh_token, httponly=True, expires=refresh_expires.total_seconds())

    return {"message": "Token refreshed successfully"}


@app.get("/admin")
def admin_endpoint(
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough privileges")
    return {"msg": "Welcome admin!"}


@app.get("/error")
def raise_error():
    """Endpoint used in tests to trigger error handling."""
    raise RuntimeError("boom")


# Post Endpoints
@app.post("/users/{user_id}/posts/", response_model=schemas.Post)
def create_post_for_user(
    user_id: int,
    post: schemas.PostCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
    csrf_protect: CsrfProtect = Depends()
):
    csrf_protect.validate_csrf(request)
    if not current_user or current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to create post for this user")
    return crud.create_user_post(db=db, post=post, user_id=user_id)


@app.get("/posts/", response_model=list[schemas.Post])
def read_posts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    posts = crud.get_posts(db, skip=skip, limit=limit)
    return posts


@app.get("/posts/{post_id}", response_model=schemas.Post)
def read_post(post_id: int, db: Session = Depends(get_db)):
    db_post = crud.get_post(db, post_id=post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return db_post


@app.delete("/posts/{post_id}")
def delete_post_by_id(
    post_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
    csrf_protect: CsrfProtect = Depends()
):
    csrf_protect.validate_csrf(request)
    db_post = crud.get_post(db, post_id=post_id)

    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    if not current_user or db_post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this post")

    if crud.delete_post(db, post_id=post_id):
        return {"message": "Post deleted successfully"}
    raise HTTPException(status_code=500, detail="Failed to delete post")


@app.post("/logout")
def logout(response: Response, request: Request, csrf_protect: CsrfProtect = Depends()):
    csrf_protect.validate_csrf(request)
    csrf_protect.unset_access_cookies(response)
    csrf_protect.unset_refresh_cookies(response)
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    return {"message": "Logged out successfully"}


settings = get_settings()

@app.post("/auth/google")
async def auth_google(response: Response, db: Session = Depends(get_db), id_token_str: str = Depends(schemas.GoogleIdToken), csrf_protect: CsrfProtect = Depends()):
    try:
        # Specify the CLIENT_ID of the app that accesses the backend:
        idinfo = id_token.verify_oauth2_token(id_token_str, google_requests.Request(), settings.GOOGLE_CLIENT_ID)

        # Or, if multiple clients access the backend server:
        # idinfo = id_token.verify_oauth2_token(id_token_str, google_requests.Request())
        # if idinfo['aud'] not in [CLIENT_ID_1, CLIENT_ID_2, CLIENT_ID_3]:
        #     raise ValueError('Could not verify audience.')

        # If auth request is from a G Suite domain:
        # if idinfo['hd'] == 'myblogger.com':
        #     raise ValueError('Wrong hosted domain.')

        # userid = idinfo['sub'] # Removed unused variable
        email = idinfo['email']
        username = email.split('@')[0] # Use email prefix as username for simplicity

        user = crud.get_user_by_username(db, username)
        if not user:
            # Create user if not exists. For social logins, password can be random or not set.
            user_create = schemas.UserCreate(username=username, password="social_login_password", role="user")
            user = crud.create_user(db, user_create)

        access_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        access_token = create_access_token({"sub": user.username}, expires_delta=access_expires)
        refresh_token = create_refresh_token({"sub": user.username}, expires_delta=refresh_expires)

        csrf_protect.set_access_cookies(access_token, response)
        csrf_protect.set_refresh_cookies(refresh_token, response)
        response.set_cookie(key="access_token", value=access_token, httponly=True, expires=access_expires.total_seconds())
        response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, expires=refresh_expires.total_seconds())

        return {"message": "Google login successful"}

    except ValueError: # Invalid token
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Google ID token")
    except Exception as e:
        log.exception("Error during Google authentication", exc_info=e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error during Google authentication")


@app.post("/mfa/setup")
async def setup_mfa(
    request: Request,
    current_user: models.User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db),
    csrf_protect: CsrfProtect = Depends()
):
    csrf_protect.validate_csrf(request)
    if current_user.mfa_enabled:
        raise HTTPException(status_code=400, detail="MFA is already enabled for this user")

    secret = pyotp.random_base32()
    crud.update_user_mfa_secret(db, current_user, secret)

    # Generate QR code
    totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=current_user.username, issuer_name="WebTemplateApp"
    )
    img = qrcode.make(totp_uri)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    qr_code_base64 = b64encode(buf.getvalue()).decode("utf-8")

    return {"secret": secret, "qr_code": f"data:image/png;base64,{qr_code_base64}"}


@app.post("/mfa/verify-and-enable")
async def verify_and_enable_mfa(
    mfa_data: schemas.MFAEnable,
    request: Request,
    current_user: models.User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db),
    csrf_protect: CsrfProtect = Depends()
):
    csrf_protect.validate_csrf(request)
    if not current_user.mfa_secret:
        raise HTTPException(status_code=400, detail="MFA setup not initiated")

    totp = pyotp.TOTP(current_user.mfa_secret)
    if not totp.verify(mfa_data.code):
        raise HTTPException(status_code=400, detail="Invalid TOTP code")

    crud.set_user_mfa_enabled(db, current_user, True)
    return {"message": "MFA enabled successfully"}


@app.post("/mfa/disable")
async def disable_mfa(
    request: Request,
    current_user: models.User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db),
    csrf_protect: CsrfProtect = Depends()
):
    csrf_protect.validate_csrf(request)
    if not current_user.mfa_enabled:
        raise HTTPException(status_code=400, detail="MFA is not enabled for this user")

    crud.set_user_mfa_enabled(db, current_user, False)
    crud.update_user_mfa_secret(db, current_user, None) # Clear secret
    return {"message": "MFA disabled successfully"}


# Modify login endpoint to require MFA if enabled
@app.post("/login", dependencies=[Depends(RateLimiter(times=5, seconds=60))])
def login(form_data: schemas.UserLogin, response: Response, db: Session = Depends(get_db), csrf_protect: CsrfProtect = Depends()):
    user = crud.get_user_by_username(db, form_data.username)
    if not user or not crud.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if user.mfa_enabled:
        # If MFA is enabled, require a TOTP code for full login
        if not form_data.mfa_code:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="MFA code required")
        totp = pyotp.TOTP(user.mfa_secret)
        if not totp.verify(form_data.mfa_code):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid MFA code")

    access_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    access_token = create_access_token({"sub": user.username}, expires_delta=access_expires)
    refresh_token = create_refresh_token({"sub": user.username}, expires_delta=refresh_expires)

    csrf_protect.set_access_cookies(access_token, response)
    csrf_protect.set_refresh_cookies(refresh_token, response)
    response.set_cookie(key="access_token", value=access_token, httponly=True, expires=access_expires.total_seconds())
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, expires=refresh_expires.total_seconds())

    return {"message": "Login successful"}
