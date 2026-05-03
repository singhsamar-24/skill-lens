from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from app.core.oauth import oauth
from app.core.settings import get_settings
from app.core.security import create_access_token, decode_access_token
from app.core.users import create_user, authenticate_user
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

settings = get_settings()
router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()


class SignupRequest(BaseModel):
    username: str
    email: str | None = None
    password: str


class SigninRequest(BaseModel):
    username: str
    password: str


@router.get("/github/login")
async def github_login(request: Request):
    redirect_uri = f"{settings.backend_url}{settings.api_prefix}/auth/github/callback"
    return await oauth.github.authorize_redirect(request, redirect_uri)

@router.get("/github/callback")
async def github_callback(request: Request):
    try:
        token = await oauth.github.authorize_access_token(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OAuth failed: {str(e)}")
    
    user_info = await oauth.github.get("user", token=token)
    profile = user_info.json()
    
    # Extract data
    username = profile.get("login")
    email = profile.get("email")
    avatar = profile.get("avatar_url")
    
    if not username:
        raise HTTPException(status_code=400, detail="Could not retrieve username from GitHub")

    # Create JWT
    jwt_token = create_access_token({
        "sub": username,
        "email": email,
        "avatar": avatar
    })
    
    # Redirect to frontend dashboard with token
    return RedirectResponse(url=f"{settings.frontend_url}/dashboard?token={jwt_token}")


@router.get("/google/login")
async def google_login(request: Request):
    redirect_uri = f"{settings.backend_url}{settings.api_prefix}/auth/google/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback")
async def google_callback(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OAuth failed: {str(e)}")

    user_info = await oauth.google.get("userinfo", token=token)
    profile = user_info.json()

    # Extract data
    email = profile.get("email")
    name = profile.get("name") or email
    avatar = profile.get("picture")

    if not email:
        raise HTTPException(status_code=400, detail="Could not retrieve email from Google")

    username = email.split("@")[0]

    jwt_token = create_access_token({
        "sub": username,
        "email": email,
        "avatar": avatar,
    })

    return RedirectResponse(url=f"{settings.frontend_url}/dashboard?token={jwt_token}")

@router.get("/me")
async def get_me(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return {
        "username": payload.get("sub"),
        "email": payload.get("email"),
        "avatar": payload.get("avatar")
    }


@router.post("/signup")
async def signup(body: SignupRequest):
    try:
        user = create_user(body.username, body.email, body.password)
    except ValueError as e:
        if str(e) == "username_taken":
            raise HTTPException(status_code=400, detail="Username already taken")
        raise HTTPException(status_code=400, detail=str(e))

    token = create_access_token({"sub": user["username"], "email": user.get("email")})
    return {"token": token, "user": user}


@router.post("/signin")
async def signin(body: SigninRequest):
    user = authenticate_user(body.username, body.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_access_token({"sub": user["username"], "email": user.get("email")})
    return {"token": token, "user": user}


@router.post("/logout")
async def logout(request: Request):
    # With stateless JWTs there's nothing server-side to revoke by default.
    # Clear any server session state and return success so clients can clear local tokens.
    try:
        request.session.clear()
    except Exception:
        pass
    return {"ok": True}
