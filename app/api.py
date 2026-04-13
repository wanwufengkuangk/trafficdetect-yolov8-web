from __future__ import annotations

import cv2
import numpy as np
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, WebSocket, WebSocketDisconnect

from app.inference import obstacle_service, traffic_service, yolo_service


api_router = APIRouter()


def build_config_payload(module: str) -> dict:
    service = traffic_service if module == "traffic" else obstacle_service
    return service.config_payload()


async def detect_image_with_service(
    service,
    file: UploadFile,
    conf: float,
    iou: float,
    show_labels: bool,
) -> dict:
    try:
        image = await file.read()
        return service.predict_image_bytes(image, conf=conf, iou=iou, show_labels=show_labels)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


async def export_batch_with_service(
    service,
    files: list[UploadFile],
    conf: float,
    iou: float,
    show_labels: bool,
) -> dict:
    if not files:
        raise HTTPException(status_code=400, detail="no files were uploaded")

    try:
        ordered_inputs: list[tuple[str, bytes]] = []
        for upload in sorted(files, key=lambda item: (item.filename or "").replace("\\", "/")):
            ordered_inputs.append((upload.filename or "frame.png", await upload.read()))
        return service.export_sequence(ordered_inputs, conf=conf, iou=iou, show_labels=show_labels)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


async def stream_with_service(websocket: WebSocket, service) -> None:
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
            await websocket.send_text(service.predict_frame(frame, conf=conf, iou=iou, show_labels=show_labels))
    except FileNotFoundError as exc:
        await websocket.send_json({"error": str(exc)})
        await websocket.close(code=1011)
    except WebSocketDisconnect:
        return


@api_router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@api_router.get("/config")
async def get_config() -> dict:
    return build_config_payload("traffic")


@api_router.get("/obstacle/config")
async def get_obstacle_config() -> dict:
    return build_config_payload("obstacle")


@api_router.post("/detect/image")
async def detect_image(
    file: UploadFile = File(...),
    conf: float = Form(0.25),
    iou: float = Form(0.45),
    show_labels: bool = Form(True),
) -> dict:
    return await detect_image_with_service(yolo_service, file, conf, iou, show_labels)


@api_router.post("/obstacle/detect/image")
async def detect_obstacle_image(
    file: UploadFile = File(...),
    conf: float = Form(0.25),
    iou: float = Form(0.45),
    show_labels: bool = Form(True),
) -> dict:
    return await detect_image_with_service(obstacle_service, file, conf, iou, show_labels)


@api_router.post("/obstacle/detect/batch")
async def detect_obstacle_batch(
    files: list[UploadFile] = File(...),
    conf: float = Form(0.25),
    iou: float = Form(0.45),
    show_labels: bool = Form(True),
) -> dict:
    return await export_batch_with_service(obstacle_service, files, conf, iou, show_labels)


@api_router.websocket("/ws/video")
async def websocket_video(websocket: WebSocket) -> None:
    await stream_with_service(websocket, traffic_service)
