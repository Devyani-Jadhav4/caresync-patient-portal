from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
import jwt
import mysql.connector

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="CareSync Authentication API",
    description="Authentication and role-based dashboard APIs",
    version="1.0.0"
)


# ============================================================
# CONFIGURATION
# ============================================================

# Change these according to your MySQL setup
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Admin@@12345",
    "database": "caresync"
}

SECRET_KEY = "caresync-secret-key-change-this"
ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


# ============================================================
# SECURITY
# ============================================================

security = HTTPBearer()


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_db():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except mysql.connector.Error as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database connection failed: {str(e)}"
        )


# ============================================================
# PYDANTIC MODELS
# ============================================================

class RegisterRequest(BaseModel):
    email: str
    password: str
    role: str
    linked_id: int


class LoginRequest(BaseModel):
    email: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: Optional[str] = None


# ============================================================
# PASSWORD FUNCTIONS
# ============================================================

def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")

    hashed = bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt()
    )

    return hashed.decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(
        password.encode("utf-8"),
        password_hash.encode("utf-8")
    )


# ============================================================
# JWT FUNCTIONS
# ============================================================

def create_access_token(user_id: int, role: str):
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "role": role,
        "type": "access",
        "exp": expire
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def create_refresh_token(user_id: int, role: str):
    expire = datetime.now(timezone.utc) + timedelta(
        days=REFRESH_TOKEN_EXPIRE_DAYS
    )

    payload = {
        "sub": str(user_id),
        "role": role,
        "type": "refresh",
        "exp": expire
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def decode_token(token: str):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


# ============================================================
# GET CURRENT USER
# ============================================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    payload = decode_token(token)

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=401,
            detail="Access token required"
        )

    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    connection = get_db()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT
                user_id,
                email,
                role,
                linked_id,
                is_active,
                created_at
            FROM users
            WHERE user_id = %s
            """,
            (user_id,)
        )

        user = cursor.fetchone()

    finally:
        cursor.close()
        connection.close()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    if not user["is_active"]:
        raise HTTPException(
            status_code=403,
            detail="User account is inactive"
        )

    return user


# ============================================================
# 1. REGISTER
# ============================================================

@app.post("/register")
def register(data: RegisterRequest):

    # Validate role
    allowed_roles = {"doctor", "patient", "billing"}

    if data.role not in allowed_roles:
        raise HTTPException(
            status_code=400,
            detail="Role must be doctor, patient, or billing"
        )

    connection = get_db()
    cursor = connection.cursor(dictionary=True)

    try:

        # Check whether email already exists
        cursor.execute(
            "SELECT user_id FROM users WHERE email = %s",
            (data.email,)
        )

        existing_user = cursor.fetchone()

        if existing_user:
            raise HTTPException(
                status_code=409,
                detail="Email already registered"
            )

        # Hash password
        password_hash = hash_password(data.password)

        # Insert user
        cursor.execute(
            """
            INSERT INTO users
            (
                email,
                password_hash,
                role,
                linked_id,
                is_active
            )
            VALUES (%s, %s, %s, %s, 1)
            """,
            (
                data.email,
                password_hash,
                data.role,
                data.linked_id
            )
        )

        connection.commit()

        user_id = cursor.lastrowid

        return {
            "message": "User registered successfully",
            "user_id": user_id,
            "email": data.email,
            "role": data.role,
            "linked_id": data.linked_id
        }

    except mysql.connector.Error as e:

        connection.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )

    finally:
        cursor.close()
        connection.close()


# ============================================================
# 2. LOGIN
# ============================================================

@app.post("/login")
def login(data: LoginRequest):

    connection = get_db()
    cursor = connection.cursor(dictionary=True)

    try:

        cursor.execute(
            """
            SELECT
                user_id,
                email,
                password_hash,
                role,
                linked_id,
                is_active
            FROM users
            WHERE email = %s
            """,
            (data.email,)
        )

        user = cursor.fetchone()

    finally:
        cursor.close()
        connection.close()

    if not user:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not user["is_active"]:

        raise HTTPException(
            status_code=403,
            detail="User account is inactive"
        )

    # Check password
    if not verify_password(
        data.password,
        user["password_hash"]
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Create tokens
    access_token = create_access_token(
        user["user_id"],
        user["role"]
    )

    refresh_token = create_refresh_token(
        user["user_id"],
        user["role"]
    )

    return {
        "message": "Login successful",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "user_id": user["user_id"],
            "email": user["email"],
            "role": user["role"],
            "linked_id": user["linked_id"]
        }
    }


# ============================================================
# 3. REFRESH TOKEN
# ============================================================

@app.post("/refresh")
def refresh_token(data: RefreshRequest):

    payload = decode_token(data.refresh_token)

    if payload.get("type") != "refresh":

        raise HTTPException(
            status_code=401,
            detail="Refresh token required"
        )

    user_id = payload.get("sub")
    role = payload.get("role")

    if not user_id or not role:

        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token"
        )

    # Check user still exists and is active
    connection = get_db()
    cursor = connection.cursor(dictionary=True)

    try:

        cursor.execute(
            """
            SELECT user_id, role, is_active
            FROM users
            WHERE user_id = %s
            """,
            (user_id,)
        )

        user = cursor.fetchone()

    finally:
        cursor.close()
        connection.close()

    if not user:

        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    if not user["is_active"]:

        raise HTTPException(
            status_code=403,
            detail="User account is inactive"
        )

    # Create new access token
    new_access_token = create_access_token(
        user["user_id"],
        user["role"]
    )

    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }


# ============================================================
# 4. LOGOUT
# ============================================================

@app.post("/logout")
def logout(
    data: LogoutRequest,
    current_user: dict = Depends(get_current_user)
):

    # For this basic implementation, logout is handled
    # on the client by deleting the stored access/refresh tokens.

    return {
        "message": "Logout successful",
        "user_id": current_user["user_id"]
    }


# ============================================================
# 5. GET CURRENT USER
# ============================================================

@app.get("/me")
def get_me(
    current_user: dict = Depends(get_current_user)
):

    return {
        "user": current_user
    }


# ============================================================
# 6. DOCTOR DASHBOARD
# ============================================================

@app.get("/dashboard/doctor")
def doctor_dashboard(
    current_user: dict = Depends(get_current_user)
):

    if current_user["role"] != "doctor":

        raise HTTPException(
            status_code=403,
            detail="Doctor access required"
        )

    return {
        "message": "Welcome to Doctor Dashboard",
        "user": {
            "user_id": current_user["user_id"],
            "email": current_user["email"],
            "role": current_user["role"],
            "linked_id": current_user["linked_id"]
        },
        "dashboard": {
            "appointments": [],
            "patients": [],
            "message": "Doctor dashboard data will appear here."
        }
    }


# ============================================================
# 7. PATIENT DASHBOARD
# ============================================================

@app.get("/dashboard/patient")
def patient_dashboard(
    current_user: dict = Depends(get_current_user)
):

    if current_user["role"] != "patient":

        raise HTTPException(
            status_code=403,
            detail="Patient access required"
        )

    return {
        "message": "Welcome to Patient Dashboard",
        "user": {
            "user_id": current_user["user_id"],
            "email": current_user["email"],
            "role": current_user["role"],
            "linked_id": current_user["linked_id"]
        },
        "dashboard": {
            "appointments": [],
            "records": [],
            "message": "Patient dashboard data will appear here."
        }
    }


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "message": "CareSync Authentication API is running",
        "docs": "/docs"
    }