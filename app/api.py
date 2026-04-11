from __future__ import annotations

import cv2
import numpy as np
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, WebSocket, WebSocketDisconnect

from app.inference import yolo_service


api_router = APIRouter()


@api_router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@api_router.get("/config")
async def get_config() -> dict:
    config = yolo_service.runtime_config
    return {
        "project_name": config.project_name,
        "web_title": config.web_title,
        "classes": config.class_names,
        "ch_classes": config.class_names_zh,
        "default_conf": config.default_conf,
        "default_iou": config.default_iou,
    }


@api_router.post("/detect/image")
async def detect_image(
    file: UploadFile = File(...),
    conf: float = Form(0.25),
    iou: float = Form(0.45),
    show_labels: bool = Form(True),
) -> dict:
    try:
        image = await file.read()
        encoded, detections = yolo_service.predict_image_bytes(image, conf=conf, iou=iou, show_labels=show_labels)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {"image": encoded, "detections": detections}


@api_router.websocket("/ws/video")
async def websocket_video(websocket: WebSocket) -> None:
    await websocket.accept()
    conf = float(websocket.query_params.get("conf", "0.25"))
    iou = float(websocket.query_params.get("iou", "0.45"))
    show_labels = websocket.query_params.get("show_labels", "true").lower() == "true"
    try:
        while True:
            payload = await websocket.receive_bytes()
            frame = cv2.imdecode(np.frombuffer(payload, np.uint8), cv2.IMREAD_COLOR)
            if frame is None:
                continue
            await websocket.send_text(yolo_service.predict_frame(frame, conf=conf, iou=iou, show_labels=show_labels))
    except FileNotFoundError as exc:
        await websocket.send_json({"error": str(exc)})
        await websocket.close(code=1011)
    except WebSocketDisconnect:
        return

