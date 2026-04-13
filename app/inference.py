from __future__ import annotations

import base64
import csv
import json
import re
import shutil
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

import cv2
import numpy as np
from ultralytics import YOLO

from app.config import ModuleConfig, RuntimeConfig, load_runtime_config
from models.register import register_all

PREVIEW_FRAME_LIMIT = 8
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


@dataclass(frozen=True)
class DetectionResult:
    class_id: int
    class_name: str
    class_name_zh: str
    confidence: float
    bbox: list[float]


def encode_image(image: np.ndarray) -> str:
    ok, buffer = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, 90])
    if not ok:
        raise RuntimeError("failed to encode image")
    return base64.b64encode(buffer).decode("utf-8")


def decode_image(image_bytes: bytes) -> np.ndarray:
    image_array = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("invalid image payload")
    return image


def normalize_upload_name(name: str) -> str:
    return name.replace("\\", "/")


def is_supported_image_name(name: str) -> bool:
    return Path(name).suffix.lower() in IMAGE_EXTENSIONS


def sanitize_path_token(value: str) -> str:
    normalized = re.sub(r"[^0-9A-Za-z_-]+", "_", value.strip())
    normalized = normalized.strip("_")
    return normalized or "sequence"


def build_detection_summary(detections: Iterable[dict[str, Any]]) -> dict[str, Any]:
    normalized = list(detections)
    return {
        "detection_count": len(normalized),
        "max_confidence": round(float(max((item["confidence"] for item in normalized), default=0.0)), 6),
    }


class BaseYOLOModuleService:
    def __init__(self, module_key: str, runtime_config: RuntimeConfig | None = None) -> None:
        self.runtime_config = runtime_config or load_runtime_config()
        self.module_key = module_key
        self.module_config: ModuleConfig = self.runtime_config.modules[module_key]
        self.model: YOLO | None = None
        self.model_path: Path | None = None

    def resolve_model_path(self, model_path: str | Path | None = None) -> Path:
        if model_path is not None:
            resolved = Path(model_path).resolve()
        else:
            resolved = self.runtime_config.module_weight_path(self.module_key).resolve()
        if not resolved.exists():
            raise FileNotFoundError(f"model checkpoint not found: {resolved}")
        return resolved

    def ensure_loaded(self) -> None:
        if self.model is None:
            self.load_model()

    def load_model(self, model_path: str | Path | None = None) -> None:
        raise NotImplementedError

    def config_payload(self) -> dict[str, Any]:
        payload = {
            "module": self.module_key,
            "project_name": self.runtime_config.project_name,
            "web_title": self.runtime_config.web_title,
            "module_title": self.module_config.title,
            "module_subtitle": self.module_config.subtitle,
            "classes": self.module_config.class_names,
            "ch_classes": self.module_config.class_names_zh,
            "default_conf": self.runtime_config.default_conf,
            "default_iou": self.runtime_config.default_iou,
            "task": self.module_config.task,
            "supports_batch": self.module_config.supports_batch,
            "supports_stream": self.module_config.supports_stream,
            "supports_boxes": self.module_config.supports_boxes,
            "supports_masks": self.module_config.supports_masks,
            "supports_sequence_input": self.module_config.supports_sequence_input,
        }
        if self.module_config.sequence_input_mode is not None:
            payload["sequence_input_mode"] = self.module_config.sequence_input_mode
        if self.module_config.sequence_playback_mode is not None:
            payload["sequence_playback_mode"] = self.module_config.sequence_playback_mode
        return payload

    def results_url_for(self, path: Path) -> str:
        relative = path.resolve().relative_to(self.runtime_config.results_dir.resolve())
        return "/results/" + PurePosixPath(relative.as_posix()).as_posix()


class DetectionModuleService(BaseYOLOModuleService):
    use_custom_register = False

    def load_model(self, model_path: str | Path | None = None) -> None:
        resolved = self.resolve_model_path(model_path)
        if self.model is not None and self.model_path == resolved:
            return
        if self.use_custom_register:
            register_all(use_wiou=False)
        self.model = YOLO(str(resolved))
        self.model_path = resolved

    def format_detections(self, prediction: Any) -> list[dict[str, Any]]:
        detections: list[dict[str, Any]] = []
        for box in prediction.boxes:
            class_id = int(box.cls[0])
            detections.append(
                asdict(
                    DetectionResult(
                        class_id=class_id,
                        class_name=self.module_config.class_names[class_id],
                        class_name_zh=self.module_config.class_names_zh[class_id],
                        confidence=round(float(box.conf[0]), 6),
                        bbox=[round(float(value), 3) for value in box.xyxy[0].tolist()],
                    )
                )
            )
        return detections

    def predict_image_array(
        self,
        image: np.ndarray,
        conf: float,
        iou: float,
        show_labels: bool = True,
    ) -> tuple[np.ndarray, list[dict[str, Any]], dict[str, Any]]:
        self.ensure_loaded()
        assert self.model is not None
        prediction = self.model.predict(source=image, conf=conf, iou=iou, verbose=False)[0]
        detections = self.format_detections(prediction)
        summary = build_detection_summary(detections)
        rendered = prediction.plot(
            labels=show_labels,
            boxes=self.module_config.supports_boxes,
        )
        return rendered, detections, summary

    def predict_image_bytes(
        self,
        image_bytes: bytes,
        conf: float,
        iou: float,
        show_labels: bool = True,
    ) -> dict[str, Any]:
        image = decode_image(image_bytes)
        rendered, detections, summary = self.predict_image_array(image, conf=conf, iou=iou, show_labels=show_labels)
        return {"image": encode_image(rendered), "detections": detections, "summary": summary}

    def predict_frame(self, frame: np.ndarray, conf: float, iou: float, show_labels: bool = True) -> str:
        rendered, _, _ = self.predict_image_array(frame, conf=conf, iou=iou, show_labels=show_labels)
        return encode_image(rendered)


class TrafficDetectionService(DetectionModuleService):
    use_custom_register = True


class AnimalDetectionService(DetectionModuleService):
    def build_job_name(self, first_filename: str) -> str:
        normalized_name = normalize_upload_name(first_filename)
        folder_token = PurePosixPath(normalized_name).parts[0] if "/" in normalized_name else Path(normalized_name).stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{sanitize_path_token(folder_token)}_{timestamp}"

    def export_sequence(
        self,
        frames: list[tuple[str, bytes]],
        conf: float,
        iou: float,
        show_labels: bool = True,
    ) -> dict[str, Any]:
        valid_frames = [(normalize_upload_name(name), payload) for name, payload in frames if is_supported_image_name(name)]
        if not valid_frames:
            raise ValueError("no supported image files were uploaded")

        valid_frames.sort(key=lambda item: item[0])
        job_name = self.build_job_name(valid_frames[0][0])
        job_dir = self.runtime_config.results_dir / "animal_sequences" / job_name
        rendered_dir = job_dir / "rendered"
        rendered_dir.mkdir(parents=True, exist_ok=True)

        frame_rows: list[dict[str, Any]] = []
        positive_frame_count = 0
        detection_counts: list[int] = []
        max_confidences: list[float] = []

        for index, (file_name, payload) in enumerate(valid_frames, start=1):
            image = decode_image(payload)
            rendered, detections, summary = self.predict_image_array(image, conf=conf, iou=iou, show_labels=show_labels)
            render_name = f"{index:05d}__{Path(file_name).stem}.jpg"
            rendered_path = rendered_dir / render_name
            if not cv2.imwrite(str(rendered_path), rendered):
                raise RuntimeError(f"failed to write rendered frame: {rendered_path}")

            positive = summary["detection_count"] > 0
            if positive:
                positive_frame_count += 1
            detection_counts.append(int(summary["detection_count"]))
            max_confidences.append(float(summary["max_confidence"]))
            frame_rows.append(
                {
                    "frame_index": index,
                    "file_name": file_name,
                    "rendered_url": self.results_url_for(rendered_path),
                    "positive": positive,
                    "detection_count": summary["detection_count"],
                    "max_confidence": summary["max_confidence"],
                    "detections": detections,
                }
            )

        manifest_path = job_dir / "manifest.json"
        summary_path = job_dir / "summary.json"
        csv_path = job_dir / "summary.csv"
        archive_base = job_dir / "animal_sequence"

        summary_payload = {
            "job_name": job_name,
            "frame_count": len(frame_rows),
            "positive_frame_count": positive_frame_count,
            "average_detections_per_frame": round(float(sum(detection_counts) / len(detection_counts)), 6) if detection_counts else 0.0,
            "max_detection_count": int(max(detection_counts, default=0)),
            "max_confidence": round(float(max(max_confidences, default=0.0)), 6),
        }
        manifest_payload = {
            "job_name": job_name,
            "frames": frame_rows,
        }

        manifest_path.write_text(json.dumps(manifest_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        summary_path.write_text(json.dumps(summary_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        with csv_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                extrasaction="ignore",
                fieldnames=[
                    "frame_index",
                    "file_name",
                    "rendered_url",
                    "positive",
                    "detection_count",
                    "max_confidence",
                ],
            )
            writer.writeheader()
            writer.writerows(frame_rows)

        archive_path = Path(shutil.make_archive(str(archive_base), "zip", root_dir=str(job_dir), base_dir="."))
        preview_candidates = [row for row in frame_rows if row["positive"]] or frame_rows
        preview = preview_candidates[:PREVIEW_FRAME_LIMIT]

        return {
            "job_name": job_name,
            "frame_count": len(frame_rows),
            "positive_frame_count": positive_frame_count,
            "output_dir": self.results_url_for(job_dir),
            "archive_path": self.results_url_for(archive_path),
            "csv_path": self.results_url_for(csv_path),
            "summary_path": self.results_url_for(summary_path),
            "manifest_path": self.results_url_for(manifest_path),
            "preview": preview,
        }


shared_runtime_config = load_runtime_config()
traffic_service = TrafficDetectionService(module_key="traffic", runtime_config=shared_runtime_config)
obstacle_service = AnimalDetectionService(module_key="obstacle", runtime_config=shared_runtime_config)
yolo_service = traffic_service
