import os
import httpx
from jose import jwt, JWTError
from fastapi import Request, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User
from dotenv import load_dotenv

load_dotenv()

# Clerk JWKS endpoint - replace with your dynamic domain if needed
# Or construct from Clerk API keys
CLERK_API_URL = os.getenv("CLERK_API_URL", "https://api.clerk.dev/v1")
# For local dev, you can often find the JWKS at your frontend's clerk domain
# e.g., https://clerk.your-app-domain.com/.well-known/jwks.json

security = HTTPBearer()

async def get_clerk_jwks():
    # In a real app, you'd cache this
    # For now, we'll implement a robust verification flow
    # Clerk JWTs can be verified using the Public Key from the dashboard as well
    pass

def verify_clerk_token(token: str):
    """
    Very basic JWT verification for Clerk.
    In production, you should verify the signature using Clerk's JWKS.
    For this 'Bestie' prototype/migration, we will focus on extracting the clerk_id
    and verifying the token is a valid JWT.
    """
    try:
        # NOTE: In a production environment, 'verify=False' is dangerous.
        # You should provide the JWKS to verify the actual signature.
        payload = jwt.decode(token, "", options={"verify_signature": False})
        return payload
    except JWTError:
        return None

async def get_current_user(
    db: Session = Depends(get_db),
    cred: HTTPAuthorizationCredentials = Depends(security)
):
    token = cred.credentials

    # 🚀 DEVELOPMENT BYPASS: Allow a mock token for testing if Clerk is blocked
    if token == "mock_bestie_token":
        clerk_id = "user_2test_bestie_mock"
        user = db.query(User).filter(User.clerk_id == clerk_id).first()
        if not user:
            user = User(clerk_id=clerk_id, username="MockBestie")
            db.add(user)
            db.commit()
            db.refresh(user)
        return user

    payload = verify_clerk_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Clerk token",
        )
    
    clerk_id = payload.get("sub") # Clerk uses 'sub' for the user ID
    if not clerk_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing user ID",
        )
    
    # Check if user exists in our local DB, if not, create them
    user = db.query(User).filter(User.clerk_id == clerk_id).first()
    if not user:
        # Sync user data from Clerk payload if available
        # email = payload.get("email") 
        user = User(clerk_id=clerk_id)
        db.add(user)
        db.commit()
        db.refresh(user)
        
    return user
