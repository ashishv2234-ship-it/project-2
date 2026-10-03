import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.core.config import settings
from app.seed.seed_data import seed_database
from app.websocket.manager import ws_manager

# Import API v1 routers
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.network import router as network_router
from app.api.v1.weather import router as weather_router
from app.api.v1.risk import router as risk_router
from app.api.v1.routes import router as routes_router
from app.api.v1.vehicles import router as vehicles_router
from app.api.v1.field_reports import router as field_reports_router
from app.api.v1.alerts import router as alerts_router
from app.api.v1.dashboards import router as dashboards_router
from app.api.v1.sync import router as sync_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure tables and seed demo data
    print("[SYSTEM] Starting NER-LogiSense Intelligence Platform Engine...")
    seed_database()
    print("[SYSTEM] System ready. All microservice modules online.")
    yield
    # Shutdown
    print("[SYSTEM] Shutting down NER-LogiSense backend.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description=r"""
# NER-LogiSense Backend API
### AI-powered Smart Logistics and Accessibility Intelligence Platform for India's North Eastern Region (NER)

**Core Capabilities**:
- Real-time road, bridge, and transport accessibility monitoring
- Landslide and flood disruption prediction using environmental feature models
- AI-based multi-criteria route optimization ($Cost = \alpha \cdot T + \beta \cdot R + \gamma \cdot C$)
- High-throughput GPS tracking of vehicles carrying medical oxygen, cryo-vaccines, foodgrains, and relief supplies
- Offline-first field hazard reporting with idempotency and conflict resolution
- Multilingual automated alerts across 9 regional languages
- WebSocket telemetry streaming
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers under /api/v1
api_prefix = settings.API_V1_STR
app.include_router(auth_router, prefix=api_prefix)
app.include_router(users_router, prefix=api_prefix)
app.include_router(network_router, prefix=api_prefix)
app.include_router(weather_router, prefix=api_prefix)
app.include_router(risk_router, prefix=api_prefix)
app.include_router(routes_router, prefix=api_prefix)
app.include_router(vehicles_router, prefix=api_prefix)
app.include_router(field_reports_router, prefix=api_prefix)
app.include_router(alerts_router, prefix=api_prefix)
app.include_router(dashboards_router, prefix=api_prefix)
app.include_router(sync_router, prefix=api_prefix)

# WebSocket Endpoints
@app.websocket("/ws/telemetry")
async def websocket_telemetry_endpoint(websocket: WebSocket):
    """Real-time live vehicle GPS coordinates, speed, heading, and cryogenic temperature stream."""
    await ws_manager.connect(websocket, channel="telemetry")
    try:
        while True:
            data = await websocket.receive_text()
            # Echo or process client ping
            await websocket.send_json({"type": "PONG", "payload": data})
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)

@app.websocket("/ws/alerts")
async def websocket_alerts_endpoint(websocket: WebSocket):
    """Real-time broadcast of new blockades, emergency activations, and incident verifications."""
    await ws_manager.connect(websocket, channel="alerts")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)

# Health Check
@app.get("/health", tags=["Health & Status"])
def health_check():
    return {
        "status": "HEALTHY",
        "service": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION,
        "environment": settings.ENVIRONMENT
    }

# Mount Frontend static files
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend"))
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    @app.get("/", include_in_schema=False)
    def serve_frontend_index():
        return FileResponse(os.path.join(frontend_dir, "index.html"))
