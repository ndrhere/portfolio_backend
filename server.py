from fastapi import FastAPI, APIRouter, HTTPException, status
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timezone


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI()
api_router = APIRouter(prefix="/api")


# ============= Models =============
class ContactSubmissionCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    subject: Optional[str] = Field(default=None, max_length=200)
    message: str = Field(min_length=1, max_length=5000)


class ContactSubmission(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: EmailStr
    subject: Optional[str] = None
    message: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ============= Routes =============
@api_router.get("/")
async def root():
    return {"message": "Portfolio API online"}


@api_router.get("/profile")
async def get_profile():
    """Static portfolio content. Could be moved to Mongo later for CMS."""
    return {
        "name": "Narendra Chawda",
        "tagline": "Full-Stack Developer",
        "role_overline": "SYS.ADMIN / FULL-STACK",
        "headline": [
            "BUILDING",
            "RESILIENT",
            "SOFTWARE",
            "FOR THE WEB.",
        ],
        "location": "Mumbai,IN",
        "years_experience": 4,
        "shipped_projects": 14,
        "open_source_commits": 580,
        "bio": (
            "I'm a full-stack engineer obsessed with shipping. I architect "
            "performant systems, design pixel-precise interfaces, and care about "
            "the boring parts: observability, testing, and developer experience. "
            "Currently building products with React, TypeScript, Node, and Postgres."
        ),
        "email": "ndrhere550@gmail.com",
        "socials": {
            "github": "https://github.com/ndrhere",
            "linkedin": "https://linkedin.com/in/narendra-chawda-0165a715b",
            "twitter": "https://twitter.com",
        },
        "skills": {
            "languages": ["TypeScript", "JavaScript", "Python", "Go", "Rust", "SQL"],
            "frameworks": ["React", "Next.js", "Node.js", "FastAPI", "Express", "Tailwind"],
            "databases": ["PostgreSQL", "MongoDB", "Redis", "DynamoDB"],
            "tools": ["Docker", "Kubernetes", "AWS", "Vercel", "Git", "Linux"],
        },
        "projects": [
            {
                "id": "p1",
                "title": "Streamify",
                "year": "2024",
                "description": (
                    "Real-time language learning social platform processing 10000+ events daily. "
                    "Built ingestion pipeline, query engine, and dashboard."
                ),
                "stack": ["React.js", "Node.js", "Express", "MongoDB"],
                "image": "https://images.unsplash.com/photo-1587522384446-64daf3e2689a",
                "live_url": "https://streamify-p5n7.onrender.com",
                "code_url": "https://github.com/ndrhere/Streamify",
            },
            {
                "id": "p2",
                "title": "Posgrestore",
                "year": "2025",
                "description": (
                    "E-Commence platform for marketing teams. Visual editor, type-safe "
                    "content models, and CDN-backed delivery."
                ),
                "stack": ["React", "Node", "Postgres", "AWS"],
                "image": "https://images.pexels.com/photos/8408538/pexels-photo-8408538.jpeg",
                "live_url": "https://posgrestore-1.onrender.com",
                "code_url": "https://github.com/ndrhere/Posgrestore",
            },
            {
                "id": "p3",
                "title": "Forge DevTools",
                "year": "2024",
                "description": (
                    "CLI + browser extension for inspecting and replaying API traffic "
                    "in local dev environments. 8k+ weekly downloads."
                ),
                "stack": ["Rust", "TypeScript", "WebExtensions"],
                "image": "https://images.pexels.com/photos/6638402/pexels-photo-6638402.png",
                "live_url": "https://example.com",
                "code_url": "https://github.com",
            },
            {
                "id": "p4",
                "title": "Nexmera - ResumeTailor",
                "year": "2026",
                "description": (
                    "AI-powered SaaS application with resume tailoring, custom downloads, "
                    "and subscription models."
                ),
                "stack": ["React", "TypeScript", "Node", "Postgres"],
                "image": "https://images.pexels.com/photos/12627677/pexels-photo-12627677.jpeg",
                "live_url": "https://www.nexmera.com",
                "code_url": "https://github.com/ndrhere/ResumeTailor-client",
            },
        ],
        "experience": [
            {
                "role": "Software Engineer",
                "company": "NeoSOFT Technologies",
                "period": "2025 — 2026",
                "summary": (
                    "Developed and maintained scalable web applications,"
                    "built REST APIs, optimized backend performance, and "
                    "collaborated with cross-functional teams. "
                ),
                "tags": ["React", "Node.js", "MongoDB", "Nest.js"],
            },
            {
                "role": "Software Engineer",
                "company": "Sigma Solve Inc",
                "period": "2025 — 2025",
                "summary": (
                    "Developed and maintained full-stack web applications,"
                    "built REST APIs, integrated third-party services,"
                    "and delivered production-ready features."
                ),
                "tags": ["React", "Node", "Postgress", "MongoDB"],
            },
            {
                "role": "Full-Stack Developer",
                "company": "E-Mech Solutions Pvt Ltd",
                "period": "2022 — 2024",
                "summary": (
                    "Built and maintained full-stack web applications, developed REST APIs,"
                    "and collaborated with cross-functional teams to deliver scalable solutions."
                ),
                "tags": ["React", "Node", "MongoDB"],
            },
            {
                "role": "Junior Developer",
                "company": "Freelance",
                "period": "2016 — 2019",
                "summary": (
                    "Worked on personal and freelance web development projects while"
                    "building a strong foundation in frontend and backend development."
                    "Focused on learning modern web technologies and software development best practices."
                ),
                "tags": ["HTML", "CSS", "JavaScript"],
            },
        ],
    }


@api_router.post("/contact", response_model=ContactSubmission, status_code=status.HTTP_201_CREATED)
async def submit_contact(payload: ContactSubmissionCreate):
    submission = ContactSubmission(**payload.model_dump())
    doc = submission.model_dump()
    doc['email'] = str(doc['email'])
    doc['created_at'] = doc['created_at'].isoformat()
    try:
        await db.contact_submissions.insert_one(doc)
    except Exception as e:
        logging.exception("Failed to persist contact submission")
        raise HTTPException(status_code=500, detail="Could not save submission") from e
    return submission


@api_router.get("/contact", response_model=List[ContactSubmission])
async def list_contacts(limit: int = 100):
    cursor = db.contact_submissions.find({}, {"_id": 0}).sort("created_at", -1).limit(limit)
    items = await cursor.to_list(limit)
    for it in items:
        if isinstance(it.get('created_at'), str):
            try:
                it['created_at'] = datetime.fromisoformat(it['created_at'])
            except ValueError:
                pass
    return items


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