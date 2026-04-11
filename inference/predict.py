from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ultralytics import YOLO

from models.register import register_all
from training.train import canonical_weight_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run command-line prediction on image, video, or directory sources.")
    parser.add_argument("--variant", choices=["baseline", "p2", "p2_cbam", "full"], default="full")
    parser.add_argument("--model", type=Path)
    parser.add_argument("--source", required=True)
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--iou", type=float, default=0.45)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--device")
    parser.add_argument("--name", default="predict")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    register_all(use_wiou=False)
    model_path = args.model.resolve() if args.model else canonical_weight_path(args.variant)
    if not model_path.exists():
        raise FileNotFoundError(f"missing checkpoint: {model_path}")

    model = YOLO(str(model_path))
    model.predict(
        source=args.source,
        conf=args.conf,
        iou=args.iou,
        imgsz=args.imgsz,
        device=args.device,
        save=True,
        project=str((PROJECT_ROOT / "results").resolve()),
        name=args.name,
        exist_ok=True,
        verbose=True,
    )


if __name__ == "__main__":
    main()
