from __future__ import annotations

import base64
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from ultralytics import YOLO

from app.config import RuntimeConfig, load_runtime_config
from models.register import register_all


@dataclass(frozen=True)
class DetectionResult:
    class_id: int
    class_name: str
    class_name_zh: str
    confidence: float
    bbox: list[float]


class YOLOService:
    def __init__(self, runtime_config: RuntimeConfig | None = None) -> None:
        self.runtime_config = runtime_config or load_runtime_config()
        self.model: YOLO | None = None
        self.model_path: Path | None = None

    def resolve_model_path(self, model_path: str | Path | None = None) -> Path:
        if model_path is not None:
            resolved = Path(model_path).resolve()
        else:
            resolved = self.runtime_config.best_weight_path.resolve()
        if not resolved.exists():
            raise FileNotFoundError(f"model checkpoint not found: {resolved}")
        return resolved

    def load_model(self, model_path: str | Path | None = None) -> None:
        resolved = self.resolve_model_path(model_path)
        if self.model is not None and self.model_path == resolved:
            return
        register_all(use_wiou=False)
        self.model = YOLO(str(resolved))
        self.model_path = resolved

    def ensure_loaded(self) -> None:
        if self.model is None:
            self.load_model()

    @staticmethod
    def encode_image(image: np.ndarray) -> str:
        ok, buffer = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, 90])
        if not ok:
            raise RuntimeError("failed to encode image")
        return base64.b64encode(buffer).decode("utf-8")

    def format_detections(self, prediction: Any) -> list[dict[str, Any]]:
        detections: list[dict[str, Any]] = []
        for box in prediction.boxes:
            class_id = int(box.cls[0])
            detections.append(
                asdict(
                    DetectionResult(
                        class_id=class_id,
                        class_name=self.runtime_config.class_names[class_id],
                        class_name_zh=self.runtime_config.class_names_zh[class_id],
                        confidence=round(float(box.conf[0]), 6),
                        bbox=[round(float(value), 3) for value in box.xyxy[0].tolist()],
                    )
                )
            )
        return detections

    def predict_image_bytes(
        self,
        image_bytes: bytes,
        conf: float,
        iou: float,
        show_labels: bool = True,
    ) -> tuple[str, list[dict[str, Any]]]:
        self.ensure_loaded()
        assert self.model is not None
        image_array = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError("invalid image payload")
        prediction = self.model.predict(source=image, conf=conf, iou=iou, verbose=False)[0]
        rendered = prediction.plot(labels=show_labels)
        return self.encode_image(rendered), self.format_detections(prediction)

    def predict_frame(self, frame: np.ndarray, conf: float, iou: float, show_labels: bool = True) -> str:
        self.ensure_loaded()
        assert self.model is not None
        prediction = self.model.predict(source=frame, conf=conf, iou=iou, verbose=False)[0]
        rendered = prediction.plot(labels=show_labels)
        return self.encode_image(rendered)


yolo_service = YOLOService()

