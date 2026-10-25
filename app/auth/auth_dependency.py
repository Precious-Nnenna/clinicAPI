from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.auth_model import User
from app.auth.auth_token import decode_access_token
from app.database import get_db

# The guard's "hands": it takes the token out of the request's
# "Authorization: Bearer <token>" header and gives us the token text.
# It does no checking at all, it only picks the token up.
# tokenUrl is only used by the /docs page, to tell its "Authorize" button
# where the login endpoint is. It does not affect how tokens are checked.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auths/login")


# ---------------------------------------------------------------
# THE GUARD: get_current_user
#
# Remember it as 4 questions:
#   1. Is the token real and unexpired?
#   2. Does it say who it belongs to?
#   3. Is that a proper id?
#   4. Does that person exist and are they active?
#
# Fail any one and you get the same 401.
# Pass all four and the route receives the user.
# ---------------------------------------------------------------
async def get_current_user(
    # FastAPI calls oauth2_scheme for us and hands over the token text.
    token: str = Depends(oauth2_scheme),
    # FastAPI calls get_db for us and hands over a database session.
    db: AsyncSession = Depends(get_db),
) -> User:
    # The "You can't come in" message, built once and reused below.
    # We use the same message for every failure, so a thief can't
    # tell WHY they were turned away. 401 means "I don't know who you are".
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # QUESTION 1: Is the token real and unexpired?
    # decode_access_token tries to open the token. If it is fake,
    # edited, or expired, it gives back None.
    # "raise" means: stop right here and send the error.
    # The route never runs.
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    # QUESTION 2: Does it say who it belongs to?
    # Inside the token is a note called "sub" holding the user's id.
    # .get() gives None (instead of crashing) if the note is missing.
    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    # QUESTION 3: Is that a proper id?
    # The id is stored as text, like "4", but the database wants a number.
    # int() converts it. If someone sneaks in "abc", int() would crash the
    # app with a 500 error, so try/except handles it calmly instead.
    try:
        user_id = int(user_id)
    except ValueError:
        raise credentials_exception

    # QUESTION 4: Does that person exist and are they active?
    # A token can stay valid for 15 minutes, but in that time the user could
    # have been deleted or blocked. So we check the database (the guest list)
    # every time. This is what stops a blocked user immediately.
    user = await db.get(User, user_id)
    if user is None or not user.is_active:
        raise credentials_exception

    # All four questions passed. Hand the full User to the route that asked.
    # The route never touches tokens, it just receives the user.
    return user