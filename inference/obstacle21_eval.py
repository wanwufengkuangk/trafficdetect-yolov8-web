from __future__ import annotations

import argparse
import json
import random
from collections import Counter
from pathlib import Path
from statistics import mean
from typing import Iterable
import sys

import cv2
from ultralytics import YOLO

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from models.register import register_all
from training.train import canonical_weight_path


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def collect_image_paths(directory: Path) -> list[Path]:
    return sorted(path for path in directory.iterdir() if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS)


def summarize_predictions(model: YOLO, image_paths: list[Path], conf: float, iou: float) -> dict:
    detection_counts: list[int] = []
    confidences: list[float] = []
    class_counts: Counter[str] = Counter()

    for image_path in image_paths:
        result = model.predict(source=str(image_path), conf=conf, iou=iou, verbose=False)[0]
        detections = len(result.boxes)
        detection_counts.append(detections)
        for box in result.boxes:
            confidences.append(float(box.conf[0]))
            class_counts[result.names[int(box.cls[0])]] += 1

    return {
        "images": len(image_paths),
        "detections_total": sum(detection_counts),
        "avg_detections_per_image": round(mean(detection_counts), 4) if detection_counts else 0.0,
        "avg_confidence": round(mean(confidences), 4) if confidences else 0.0,
        "class_counts": dict(class_counts),
    }


def save_visualizations(model: YOLO, image_paths: Iterable[Path], output_dir: Path, conf: float, iou: float) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for image_path in image_paths:
        result = model.predict(source=str(image_path), conf=conf, iou=iou, verbose=False)[0]
        rendered = result.plot()
        cv2.imwrite(str(output_dir / f"{image_path.stem}.jpg"), rendered)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate robustness on RoadObstacle21 without fabricating mAP.")
    parser.add_argument("--variant", choices=["baseline", "p2", "p2_cbam", "full"], default="full")
    parser.add_argument("--model", type=Path)
    parser.add_argument("--obstacle-dir", type=Path, default=Path("datasets/obstacle21/images"))
    parser.add_argument("--bdd-val-dir", type=Path, default=Path("datasets/bdd100k/images/val"))
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--iou", type=float, default=0.45)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--report-path", type=Path, default=Path("results/obstacle21_report.json"))
    parser.add_argument("--visual-dir", type=Path, default=Path("results/obstacle21_vis"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    register_all(use_wiou=False)
    model_path = args.model.resolve() if args.model else canonical_weight_path(args.variant)
    if not model_path.exists():
        raise FileNotFoundError(f"missing checkpoint: {model_path}")

    obstacle_dir = args.obstacle_dir.resolve()
    bdd_val_dir = args.bdd_val_dir.resolve()
    obstacle_images = collect_image_paths(obstacle_dir)
    bdd_images = collect_image_paths(bdd_val_dir)
    if not obstacle_images:
        raise FileNotFoundError(f"no obstacle images found under {obstacle_dir}")
    if not bdd_images:
        raise FileNotFoundError(f"no BDD val images found under {bdd_val_dir}")

    randomizer = random.Random(args.seed)
    bdd_sample = randomizer.sample(bdd_images, k=min(len(obstacle_images), len(bdd_images)))

    model = YOLO(str(model_path))
    obstacle_stats = summarize_predictions(model, obstacle_images, args.conf, args.iou)
    bdd_stats = summarize_predictions(model, bdd_sample, args.conf, args.iou)
    report = {
        "model": str(model_path),
        "obstacle21": obstacle_stats,
        "bdd100k_val_sample": bdd_stats,
        "delta": {
            "avg_detections_per_image": round(
                obstacle_stats["avg_detections_per_image"] - bdd_stats["avg_detections_per_image"],
                4,
            ),
            "avg_confidence": round(obstacle_stats["avg_confidence"] - bdd_stats["avg_confidence"], 4),
        },
    }

    args.report_path.parent.mkdir(parents=True, exist_ok=True)
    args.report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    save_visualizations(model, obstacle_images, args.visual_dir.resolve(), args.conf, args.iou)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
