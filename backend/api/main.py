"""
LATTICE Regulatory API — FastAPI application entrypoint.
"""
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from .database import get_regulation_count, init_db
from .routes.ai import router as ai_router
from .routes.alerts import router as alerts_router
from .routes.regulations import router as regulations_router
from .routes.sources import router as sources_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="LATTICE Regulatory API",
    version="0.1.0",
    description="Automated regulatory compliance intelligence platform. Tracks 15,000+ regulations across crypto, fintech, healthcare, insurance, and SaaS verticals.",
    openapi_tags=[
        {"name": "regulations", "description": "Regulation search, filtering, and CRUD"},
        {"name": "alerts", "description": "Deadline alerts and critical updates"},
        {"name": "sources", "description": "Regulatory source health and sync"},
        {"name": "ai", "description": "AI-powered querying and plain-language annotation"},
    ],
)

# Global scheduler reference so routes can inspect it
_scheduler = None

allowed_origins = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(regulations_router)
app.include_router(alerts_router)
app.include_router(sources_router)
app.include_router(ai_router)


@app.on_event("startup")
async def startup():
    logger.info("Initializing LATTICE database...")
    init_db()
    count = get_regulation_count()
    logger.info(f"Database ready — {count} regulations loaded")

    # Start background scheduler
    global _scheduler
    try:
        from ingestion.pipeline import IngestionPipeline
        from ingestion.scheduler import start_scheduler
        pipeline = IngestionPipeline()
        _scheduler = start_scheduler(pipeline)
        logger.info("Background scheduler started (daily sync at 06:00 UTC)")
    except Exception as e:
        logger.warning(f"Scheduler not started: {e}")


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")


@app.get("/health", tags=["health"])
def health():
    count = get_regulation_count()
    return {"status": "ok", "regulations": count, "version": "0.1.0"}
