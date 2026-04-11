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
    parser = argparse.ArgumentParser(description="Validate a trained YOLOv8 checkpoint against the rebuilt BDD100K val split.")
    parser.add_argument("--variant", choices=["baseline", "p2", "p2_cbam", "full"], default="baseline")
    parser.add_argument("--model", type=Path)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--batch", type=int, default=16)
    parser.add_argument("--device")
    return parser.parse_args()


def resolve_model_path(args: argparse.Namespace) -> Path:
    if args.model:
        return args.model.resolve()
    return canonical_weight_path(args.variant)


def main() -> None:
    args = parse_args()
    register_all(use_wiou=False)
    model_path = resolve_model_path(args)
    if not model_path.exists():
        raise FileNotFoundError(f"missing checkpoint: {model_path}")

    model = YOLO(str(model_path))
    metrics = model.val(
        data=str((PROJECT_ROOT / "configs" / "dataset_bdd100k.yaml").resolve()),
        imgsz=args.imgsz,
        batch=args.batch,
        device=args.device,
        project=str((PROJECT_ROOT / "results").resolve()),
        name=f"val_{args.variant}",
        exist_ok=True,
    )
    print(f"validated {model_path.name}")
    print(f"mAP50-95={metrics.box.map:.4f}")
    print(f"mAP50={metrics.box.map50:.4f}")


if __name__ == "__main__":
    main()
