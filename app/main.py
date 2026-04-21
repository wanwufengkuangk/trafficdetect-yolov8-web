from __future__ import annotations

import argparse
from contextlib import asynccontextmanager
from pathlib import Path
import sys

from fastapi import FastAPI
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
import uvicorn

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.api import api_router
from app.config import load_runtime_config
from app.inference import obstacle_service, traffic_service


STATIC_DIR = PROJECT_ROOT / "static"
RUNTIME_CONFIG = load_runtime_config()
RESULTS_DIR = RUNTIME_CONFIG.results_dir
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(_: FastAPI):
    for service in (traffic_service, obstacle_service):
        try:
            if service.resolve_model_path().exists():
                service.load_model()
        except FileNotFoundError:
            continue
    yield


app = FastAPI(title=RUNTIME_CONFIG.web_title, version="2.1.0", lifespan=lifespan)
app.include_router(api_router, prefix="/api")


@app.get("/favicon.ico", include_in_schema=False)
async def favicon() -> Response:
    return Response(status_code=204)


app.mount("/results", StaticFiles(directory=str(RESULTS_DIR), html=False), name="results")
app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Start the TrafficDetect web service.")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8010)
    parser.add_argument("--reload", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    local_url = f"http://127.0.0.1:{args.port}"
    localhost_url = f"http://localhost:{args.port}"
    print(f"INFO:     Open in browser: {local_url}")
    print(f"INFO:     Alternate local URL: {localhost_url}")
    uvicorn.run("app.main:app", host=args.host, port=args.port, reload=args.reload)


if __name__ == "__main__":
    main()
