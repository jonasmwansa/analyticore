from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, Depends, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import bcrypt
import jwt
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd
import io
import json
from emergentintegrations.llm.chat import LlmChat, UserMessage
import asyncio

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI()
api_router = APIRouter(prefix="/api")

security = HTTPBearer(auto_error=False)

JWT_SECRET = os.environ.get('JWT_SECRET_KEY')
JWT_ALGORITHM = os.environ.get('JWT_ALGORITHM', 'HS256')
JWT_EXPIRATION_DAYS = int(os.environ.get('JWT_EXPIRATION_DAYS', 7))

class User(BaseModel):
    user_id: str
    email: str
    name: str
    is_verified: bool = False
    created_at: datetime

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class SessionData(BaseModel):
    user_id: str
    email: str
    name: str
    session_id: str

class Project(BaseModel):
    project_id: str
    user_id: str
    name: str
    source_type: str
    status: str
    created_at: datetime
    file_path: Optional[str] = None
    row_count: Optional[int] = None
    column_count: Optional[int] = None

class ProjectCreate(BaseModel):
    name: str
    source_type: str

class DataStatistics(BaseModel):
    total_rows: int
    total_columns: int
    missing_values: Dict[str, int]
    data_types: Dict[str, str]
    numeric_stats: Optional[Dict[str, Any]] = None

class AIRecommendation(BaseModel):
    column: str
    issue: str
    recommendation: str
    action_type: str
    parameters: Optional[Dict[str, Any]] = None

class TransformationRule(BaseModel):
    column: str
    action: str
    parameters: Dict[str, Any]

async def get_current_user(request: Request, credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    token = None
    
    if request.cookies.get('session_token'):
        token = request.cookies.get('session_token')
    elif credentials:
        token = credentials.credentials
    
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get('user_id')
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user_doc = await db.users.find_one({"user_id": user_id}, {"_id": 0})
        if not user_doc:
            raise HTTPException(status_code=401, detail="User not found")
        
        return User(**user_doc)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def send_verification_email(email: str, token: str, name: str):
    frontend_url = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:3000')
    verification_link = f"{frontend_url}/verify-email?token={token}"
    
    message = MIMEMultipart("alternative")
    message["Subject"] = "Verify Your DataPulse Account"
    message["From"] = os.environ.get('DEFAULT_FROM_EMAIL')
    message["To"] = email
    
    html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
          <h2 style="color: #6366F1;">Welcome to DataPulse, {name}!</h2>
          <p>Thank you for signing up. Please verify your email address to get started.</p>
          <a href="{verification_link}" 
             style="display: inline-block; padding: 12px 24px; background-color: #6366F1; 
                    color: white; text-decoration: none; border-radius: 8px; margin: 20px 0;">
            Verify Email Address
          </a>
          <p>Or copy and paste this link into your browser:</p>
          <p style="color: #64748B; font-size: 14px;">{verification_link}</p>
          <p style="color: #94A3B8; font-size: 12px; margin-top: 30px;">
            If you didn't create this account, you can safely ignore this email.
          </p>
        </div>
      </body>
    </html>
    """
    
    message.attach(MIMEText(html, "html"))
    
    try:
        await aiosmtplib.send(
            message,
            hostname=os.environ.get('EMAIL_HOST'),
            port=int(os.environ.get('EMAIL_PORT')),
            username=os.environ.get('EMAIL_HOST_USER'),
            password=os.environ.get('EMAIL_HOST_PASSWORD'),
            use_tls=os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
        )
    except Exception as e:
        logging.error(f"Failed to send email: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to send verification email")

@api_router.post("/auth/register")
async def register(user_data: UserRegister):
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = bcrypt.hashpw(user_data.password.encode('utf-8'), bcrypt.gensalt())
    user_id = f"user_{uuid.uuid4().hex[:12]}"
    verification_token = uuid.uuid4().hex
    
    user_doc = {
        "user_id": user_id,
        "email": user_data.email,
        "name": user_data.name,
        "password_hash": hashed_password.decode('utf-8'),
        "is_verified": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.users.insert_one(user_doc)
    
    await db.verification_tokens.insert_one({
        "token": verification_token,
        "user_id": user_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat()
    })
    
    await send_verification_email(user_data.email, verification_token, user_data.name)
    
    return {"message": "Registration successful. Please check your email to verify your account."}

@api_router.get("/auth/verify-email")
async def verify_email(token: str):
    token_doc = await db.verification_tokens.find_one({"token": token})
    if not token_doc:
        raise HTTPException(status_code=400, detail="Invalid verification token")
    
    expires_at = datetime.fromisoformat(token_doc['expires_at'])
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    
    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Verification token expired")
    
    await db.users.update_one(
        {"user_id": token_doc['user_id']},
        {"$set": {"is_verified": True}}
    )
    
    await db.verification_tokens.delete_one({"token": token})
    
    return {"message": "Email verified successfully"}

@api_router.post("/auth/login")
async def login(credentials: UserLogin, response: Response):
    user_doc = await db.users.find_one({"email": credentials.email})
    if not user_doc:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not bcrypt.checkpw(credentials.password.encode('utf-8'), user_doc['password_hash'].encode('utf-8')):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not user_doc.get('is_verified', False):
        raise HTTPException(status_code=403, detail="Please verify your email first")
    
    token_payload = {
        "user_id": user_doc['user_id'],
        "email": user_doc['email'],
        "exp": datetime.now(timezone.utc) + timedelta(days=JWT_EXPIRATION_DAYS)
    }
    
    token = jwt.encode(token_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=JWT_EXPIRATION_DAYS * 24 * 60 * 60,
        path="/"
    )
    
    return {
        "user": {
            "user_id": user_doc['user_id'],
            "email": user_doc['email'],
            "name": user_doc['name']
        },
        "token": token
    }

@api_router.get("/auth/session")
async def handle_google_auth_session(session_id: str, response: Response):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
                headers={"X-Session-ID": session_id}
            ) as resp:
                if resp.status != 200:
                    raise HTTPException(status_code=401, detail="Invalid session")
                
                data = await resp.json()
        
        user_doc = await db.users.find_one({"email": data['email']}, {"_id": 0})
        
        if not user_doc:
            user_id = f"user_{uuid.uuid4().hex[:12]}"
            user_doc = {
                "user_id": user_id,
                "email": data['email'],
                "name": data['name'],
                "picture": data.get('picture'),
                "is_verified": True,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await db.users.insert_one(user_doc)
        
        token_payload = {
            "user_id": user_doc['user_id'],
            "email": user_doc['email'],
            "exp": datetime.now(timezone.utc) + timedelta(days=JWT_EXPIRATION_DAYS)
        }
        
        token = jwt.encode(token_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        
        response.set_cookie(
            key="session_token",
            value=token,
            httponly=True,
            secure=True,
            samesite="none",
            max_age=JWT_EXPIRATION_DAYS * 24 * 60 * 60,
            path="/"
        )
        
        return {
            "user": {
                "user_id": user_doc['user_id'],
                "email": user_doc['email'],
                "name": user_doc['name']
            }
        }
    except Exception as e:
        logging.error(f"Session error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process session")

@api_router.get("/auth/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@api_router.post("/auth/logout")
async def logout(response: Response):
    response.delete_cookie(key="session_token", path="/")
    return {"message": "Logged out successfully"}

@api_router.get("/projects")
async def get_projects(current_user: User = Depends(get_current_user)):
    projects = await db.projects.find({"user_id": current_user.user_id}, {"_id": 0}).to_list(100)
    for project in projects:
        if isinstance(project.get('created_at'), str):
            project['created_at'] = datetime.fromisoformat(project['created_at'])
    return projects

@api_router.post("/projects")
async def create_project(project_data: ProjectCreate, current_user: User = Depends(get_current_user)):
    project_id = f"proj_{uuid.uuid4().hex[:12]}"
    project_doc = {
        "project_id": project_id,
        "user_id": current_user.user_id,
        "name": project_data.name,
        "source_type": project_data.source_type,
        "status": "created",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.projects.insert_one(project_doc)
    project_doc['created_at'] = datetime.fromisoformat(project_doc['created_at'])
    return Project(**{k: v for k, v in project_doc.items() if k != '_id'})

@api_router.post("/projects/{project_id}/upload")
async def upload_file(
    project_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    project = await db.projects.find_one({"project_id": project_id, "user_id": current_user.user_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    contents = await file.read()
    file_path = f"/tmp/{project_id}_{file.filename}"
    
    with open(file_path, "wb") as f:
        f.write(contents)
    
    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_path)
        elif file.filename.endswith('.json'):
            df = pd.read_json(file_path)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")
        
        stats = {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "columns": df.columns.tolist(),
            "data_types": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "missing_values": df.isnull().sum().to_dict(),
            "sample_data": df.head(5).to_dict('records')
        }
        
        await db.projects.update_one(
            {"project_id": project_id},
            {"$set": {
                "file_path": file_path,
                "filename": file.filename,
                "row_count": len(df),
                "column_count": len(df.columns),
                "status": "uploaded",
                "statistics": stats
            }}
        )
        
        return {"message": "File uploaded successfully", "statistics": stats}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process file: {str(e)}")

@api_router.get("/projects/{project_id}/data")
async def get_project_data(project_id: str, current_user: User = Depends(get_current_user)):
    project = await db.projects.find_one({"project_id": project_id, "user_id": current_user.user_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if not project.get('file_path'):
        raise HTTPException(status_code=400, detail="No data uploaded yet")
    
    try:
        file_path = project['file_path']
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_path)
        elif file_path.endswith('.json'):
            df = pd.read_json(file_path)
        
        return {
            "data": df.head(100).to_dict('records'),
            "total_rows": len(df),
            "columns": df.columns.tolist()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load data: {str(e)}")

@api_router.post("/projects/{project_id}/analyze")
async def analyze_data(project_id: str, current_user: User = Depends(get_current_user)):
    project = await db.projects.find_one({"project_id": project_id, "user_id": current_user.user_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if not project.get('file_path'):
        raise HTTPException(status_code=400, detail="No data uploaded yet")
    
    try:
        file_path = project['file_path']
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_path)
        elif file_path.endswith('.json'):
            df = pd.read_json(file_path)
        
        stats = project.get('statistics', {})
        
        analysis_prompt = f"""
        You are a data cleaning expert. Analyze this dataset and provide actionable recommendations.
        
        Dataset Info:
        - Total Rows: {len(df)}
        - Total Columns: {len(df.columns)}
        - Columns: {', '.join(df.columns.tolist())}
        - Data Types: {df.dtypes.to_dict()}
        - Missing Values: {df.isnull().sum().to_dict()}
        - Duplicate Rows: {df.duplicated().sum()}
        
        For numeric columns:
        {df.describe().to_dict() if len(df.select_dtypes(include=['number']).columns) > 0 else 'No numeric columns'}
        
        Provide recommendations in JSON format as an array of objects with these fields:
        - column: column name
        - issue: what's the problem
        - recommendation: what to do
        - action_type: one of [fill_missing, remove_duplicates, convert_type, remove_outliers, rename_column]
        - parameters: object with action-specific parameters
        
        Focus on:
        1. Missing values (suggest mean/median/mode/forward-fill based on data type)
        2. Data type conversions (dates, numbers stored as strings)
        3. Outliers in numeric columns
        4. Duplicate rows
        5. Column naming improvements
        
        Return ONLY valid JSON array, no additional text.
        """
        
        chat = LlmChat(
            api_key=os.environ.get('EMERGENT_LLM_KEY'),
            session_id=f"analysis_{project_id}",
            system_message="You are a data analysis expert. Always respond with valid JSON."
        )
        chat.with_model("openai", "gpt-5.2")
        
        message = UserMessage(text=analysis_prompt)
        response = await chat.send_message(message)
        
        try:
            recommendations = json.loads(response)
        except:
            response_clean = response.strip()
            if response_clean.startswith('```json'):
                response_clean = response_clean[7:]
            if response_clean.endswith('```'):
                response_clean = response_clean[:-3]
            recommendations = json.loads(response_clean.strip())
        
        await db.projects.update_one(
            {"project_id": project_id},
            {"$set": {
                "ai_recommendations": recommendations,
                "analyzed_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        return {"recommendations": recommendations}
    except Exception as e:
        logging.error(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@api_router.post("/projects/{project_id}/transform")
async def apply_transformations(
    project_id: str,
    rules: List[TransformationRule],
    current_user: User = Depends(get_current_user)
):
    project = await db.projects.find_one({"project_id": project_id, "user_id": current_user.user_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if not project.get('file_path'):
        raise HTTPException(status_code=400, detail="No data uploaded yet")
    
    try:
        file_path = project['file_path']
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_path)
        elif file_path.endswith('.json'):
            df = pd.read_json(file_path)
        
        original_shape = df.shape
        
        for rule in rules:
            column = rule.column
            action = rule.action
            params = rule.parameters
            
            if action == "fill_missing":
                strategy = params.get('strategy', 'mean')
                if strategy == 'mean':
                    df[column].fillna(df[column].mean(), inplace=True)
                elif strategy == 'median':
                    df[column].fillna(df[column].median(), inplace=True)
                elif strategy == 'mode':
                    df[column].fillna(df[column].mode()[0], inplace=True)
                elif strategy == 'forward_fill':
                    df[column].fillna(method='ffill', inplace=True)
                elif strategy == 'constant':
                    df[column].fillna(params.get('value', 0), inplace=True)
            
            elif action == "remove_duplicates":
                df.drop_duplicates(inplace=True)
            
            elif action == "convert_type":
                target_type = params.get('target_type')
                if target_type == 'numeric':
                    df[column] = pd.to_numeric(df[column], errors='coerce')
                elif target_type == 'datetime':
                    df[column] = pd.to_datetime(df[column], errors='coerce')
                elif target_type == 'string':
                    df[column] = df[column].astype(str)
            
            elif action == "remove_outliers":
                if df[column].dtype in ['int64', 'float64']:
                    Q1 = df[column].quantile(0.25)
                    Q3 = df[column].quantile(0.75)
                    IQR = Q3 - Q1
                    lower = Q1 - 1.5 * IQR
                    upper = Q3 + 1.5 * IQR
                    df = df[(df[column] >= lower) & (df[column] <= upper)]
            
            elif action == "rename_column":
                new_name = params.get('new_name')
                if new_name:
                    df.rename(columns={column: new_name}, inplace=True)
        
        cleaned_path = file_path.replace('.csv', '_cleaned.csv').replace('.xlsx', '_cleaned.xlsx')
        
        if cleaned_path.endswith('.csv'):
            df.to_csv(cleaned_path, index=False)
        elif cleaned_path.endswith('.xlsx'):
            df.to_excel(cleaned_path, index=False)
        
        new_stats = {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "columns": df.columns.tolist(),
            "missing_values": df.isnull().sum().to_dict()
        }
        
        await db.projects.update_one(
            {"project_id": project_id},
            {"$set": {
                "cleaned_file_path": cleaned_path,
                "cleaned_statistics": new_stats,
                "status": "transformed",
                "transformed_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        return {
            "message": "Transformations applied successfully",
            "original_shape": original_shape,
            "new_shape": df.shape,
            "statistics": new_stats
        }
    except Exception as e:
        logging.error(f"Transform error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Transformation failed: {str(e)}")

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

import aiohttp