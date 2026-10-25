from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.auth_schema import UserCreate, UserOut, UserLogin, TokenOut, RefreshRequest
from sqlalchemy import select
from datetime import timedelta, datetime, timezone

from app.database import get_db
from app.auth.auth_model import User, Role, RefreshToken
from app.auth.auth_security import hash_password, DUMMY_HASH, verify_password
from app.auth.auth_token import create_access_token, generate_refresh_token, hash_refresh_token
from app.auth.auth_dependency import get_current_user
from app.config import settings


router = APIRouter(prefix="/auths", tags=["auths"])


@router.post("/register", response_model=UserOut, status_code=201)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == data.email.lower())
    result = await db.execute(stmt)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This email already exists" )

    hashed = hash_password(data.password)

    new_user = User(
        first_name=data.first_name,
        last_name=data.last_name,
        email=data.email.lower(),
        hashed_password=hashed, 
        role=Role.ADMIN,  # temporary
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user



@router.get("/", response_model=list[UserOut])
async def list_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    return result.scalars().all()



@router.post("/login", response_model = TokenOut)
async def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == form_data.username.lower())
    result = await db.execute(stmt)
    existing_user = result.scalar_one_or_none()

    # Prevent timing attack: always verify something
    hash_to_verify = existing_user.hashed_password if existing_user else DUMMY_HASH
    verified = verify_password(form_data.password, hash_to_verify)

    if not existing_user or not verified:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password" )

    # Password is correct, but the account has been blocked by an admin.
    # Checked after the password so only the real owner learns it's disabled.
    if not existing_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled",
        )

    #Once the email and password matches, create a token
    access_token = create_access_token(sub=str(existing_user.id),
    role=existing_user.role.value)

    raw_refresh_token = generate_refresh_token()

    new_refresh_token = RefreshToken(
            user_id=existing_user.id,
            token_hash=hash_refresh_token(raw_refresh_token),
            expires_at=datetime.now(timezone.utc)
            + timedelta(days=settings.refresh_token_expire_days),
        )
    
    db.add(new_refresh_token)
    await db.commit()

    return {"access_token": access_token, "refresh_token": raw_refresh_token, "token_type": "bearer"}



@router.post("/refresh", response_model=TokenOut)
async def refresh(data: RefreshRequest, db: AsyncSession = Depends(get_db)):

    # The client sends the raw token, but the database only stores hashes,
    # so hash what was sent and look that up.
    stmt = select(RefreshToken).where(RefreshToken.token_hash==hash_refresh_token(data.refresh_token))
    result = await db.execute(stmt)
    stored_token = result.scalar_one_or_none()

    # Same error for every failure, so nothing leaks about why it failed.
    # The order matters: check "not found" first, or .revoked would crash on None.
    if not stored_token or stored_token.revoked or stored_token.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    # Load the owner of this token. If the account was disabled after login,
    # they must not be able to get new tokens.
    user = await db.get(User, stored_token.user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    # Rotation: the old refresh token is now used up.
    stored_token.revoked = True

    # Issue a fresh access token.
    access_token = create_access_token(sub=str(user.id),
        role=user.role.value)
    
    # Issue a fresh refresh token. The client gets the raw value,
    # the database gets only its hash.
    raw_refresh_token = generate_refresh_token()
    
    new_refresh_token = RefreshToken(
            user_id=user.id,
            token_hash=hash_refresh_token(raw_refresh_token),
            expires_at=datetime.now(timezone.utc)
            + timedelta(days=settings.refresh_token_expire_days),
        )
    
    db.add(new_refresh_token)
    await db.commit()

    return {"access_token": access_token, "refresh_token": raw_refresh_token, "token_type": "bearer"}



@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout_user (data: RefreshRequest, db: AsyncSession = Depends(get_db)):
    # Hash what the client sent and look up the stored token.
    stmt = select(RefreshToken).where(RefreshToken.token_hash==hash_refresh_token(data.refresh_token))
    result = await db.execute(stmt)
    stored_token = result.scalar_one_or_none()

    # Revoke it if it exists. Unknown or already-revoked tokens are ignored,
    # and we still return 204 so nobody can probe which tokens are valid.
    if stored_token and not stored_token.revoked:
        stored_token.revoked = True
        await db.commit()



# Depends(get_current_user) puts the guard in front of this route.
# If the guard raises a 401, this function never runs.
# If the guard passes, current_user is already the real User object.
@router.get("/me", response_model=UserOut)
async def me(current_user: User = Depends(get_current_user)):
    return current_user
