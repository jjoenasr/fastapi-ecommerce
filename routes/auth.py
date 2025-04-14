from utils import create_access_token, verify_password, hash_password, decode_access_token
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends, HTTPException, APIRouter, status
from database import UserDocument
from models import Token, UserOut
import jwt
from typing import Annotated

router = APIRouter(prefix="/auth", tags=["auth"])

# User authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        # Decode the token to extract user information
        payload = decode_access_token(token)
        username = payload.get("sub")
        
        # Validate the user data
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
        
        # Fetch the user from the database
        user = await UserDocument.find_one(UserDocument.email == username)
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
        
        return user

    except jwt.PyJWTError as e:
        # Catch JWT decoding errors and provide a custom message
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
    
    except Exception as e:
        # Catch any unexpected exceptions and log them
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

user_depends = Annotated[UserOut, Depends(get_current_user)]

@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        # Fetch the user based on email (username)
        user = await UserDocument.find_one(UserDocument.email == form_data.username)
        
        # Handle invalid credentials
        if not user or not verify_password(form_data.password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")
        
        # Generate access token
        access_token = create_access_token(data={"sub": user.email})
        return access_token
    
    except Exception as e:
        # Catch any unexpected errors (e.g., database failure)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred during login")

@router.post("/register", response_model=UserOut)
async def register(username: str, email: str, password: str):
    try:
        # Check if the email already exists in the database
        existing_user = await UserDocument.find_one(UserDocument.email == email)
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        
        # Hash the password
        hashed_password = hash_password(password)
        
        # Create and insert the new user
        user = UserDocument(username=username, email=email, password_hash=hashed_password)
        await user.insert()
        
        return user

    except Exception as e:
        # Handle unexpected errors (e.g., database failure)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred during registration")

@router.get("/me", response_model=UserOut)
async def read_users_me(current_user: user_depends):
    try:
        return current_user
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while fetching user data")
