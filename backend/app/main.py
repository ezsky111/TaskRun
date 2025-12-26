import os
from fastapi import FastAPI
import logging
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from funboost.faas import CareProjectNameEnv

# (可选) 设置项目名，只管理本项目相关的队列，避免干扰
CareProjectNameEnv.set('my_awesome_project')

from app.routers.auth import router as auth_router
from app.routers.funboost import router as funboost_router
from app.routers.system import router as system_router

app = FastAPI()

# Include routers
app.include_router(auth_router, prefix="/api")
app.include_router(funboost_router, prefix="/api")
app.include_router(system_router, prefix="/api")

# Mount static files for frontend
frontend_path = "/frontend/dist"
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

    # Catch-all route for SPA routing
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Serve index.html for any unmatched routes (SPA routing)
        if not full_path.startswith("/api"):
            return FileResponse(os.path.join(frontend_path, "index.html"))
else:
    logging.warning(f"Frontend path {frontend_path} does not exist. Make sure frontend is built.")

