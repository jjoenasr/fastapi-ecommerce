from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends, HTTPException, APIRouter, status
from sqlmodel import Session, select
from database import User, get_session
from models import Token, UserOut, UserIn
from typing import Annotated
from supabase_client import get_supabase
from supabase import Client
import uuid

router = APIRouter(prefix="/auth", tags=["auth"])

# User authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

def get_current_user(token: str = Depends(oauth2_scheme),
                    supabase: Client = Depends(get_supabase),
                    db: Session = Depends(get_session)) -> UserOut:
    try:
        response = supabase.auth.get_user(token)
        user = response.user
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
        user_db = db.exec(select(User).where(User.email == user.email)).first()
        if not user_db:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        return user_db

    except Exception as e:
        # Catch any unexpected exceptions and log them
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

user_depends = Annotated[UserOut, Depends(get_current_user)]

@router.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), supabase: Client = Depends(get_supabase)):
    try:
        response = supabase.auth.sign_in_with_password(
            {
                "email": form_data.username, 
                "password": form_data.password
            }
        )
        if not response or not response.session:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        
        return response.session
    
    except Exception as e:
        # Catch any unexpected errors (e.g., database failure)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred during login")

@router.post("/register", response_model=UserOut)
def register(user: UserIn, db: Session = Depends(get_session), supabase: Client = Depends(get_supabase)):
    try:
        response = supabase.auth.sign_up(
            {
                "email":  user.email, 
                "password": user.password,
            }
        )
        if not response:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Supabase sign-up failed")
        user_id = uuid.UUID(response.user.id)
        if not user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User creation failed")
        
        # Assuming the user is created successfully in Supabase, we can now create a local user in our database
        existing_user = db.exec(select(User).where(User.email == user.email)).first()
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        db_user = User(id=user_id, username=user.username, email=user.email, first_name=user.first_name, last_name=user.last_name)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)  # Refresh the instance to get the updated data
        
        return db_user

    except Exception as e:
        # Handle unexpected errors (e.g., database failure)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred during registration")

@router.get("/me", response_model=UserOut)
def read_users_me(current_user: user_depends):
    try:
        return current_user
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while fetching user data")
