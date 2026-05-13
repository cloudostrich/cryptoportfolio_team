from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated, Optional
from ..models.schemas import UserCreate, UserResponse, Token
from ..services import auth
from ..db import queries

router = APIRouter(prefix="/api/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = auth.decode_access_token(token)
    if payload is None:
        raise credentials_exception
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    user = queries.get_user_by_username(username)
    if user is None:
        raise credentials_exception
    return user

oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

async def get_optional_user(token: Annotated[Optional[str], Depends(oauth2_scheme_optional)] = None):
    if token is None:
        return None
    payload = auth.decode_access_token(token)
    if payload is None:
        return None
    username: str = payload.get("sub")
    if username is None:
        return None
    return queries.get_user_by_username(username)

@router.post("/register", response_model=UserResponse)
def register(user: UserCreate):
    db_user = queries.get_user_by_username(user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    new_user = queries.create_user(
        username=user.username,
        email=user.email,
        password_hash=hashed_password
    )
    return new_user

@router.post("/login", response_model=Token)
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = queries.get_user_by_username(form_data.username)
    if not user or not auth.verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth.create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: Annotated[dict, Depends(get_current_user)]):
    return current_user
