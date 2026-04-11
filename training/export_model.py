from __future__ import annotations

import argparse
import shutil
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ultralytics import YOLO

from models.register import register_all
from training.train import canonical_weight_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export a trained checkpoint to ONNX.")
    parser.add_argument("--variant", choices=["baseline", "p2", "p2_cbam", "full"], default="full")
    parser.add_argument("--model", type=Path)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    register_all(use_wiou=False)
    model_path = args.model.resolve() if args.model else canonical_weight_path(args.variant)
    if not model_path.exists():
        raise FileNotFoundError(f"missing checkpoint: {model_path}")

    model = YOLO(str(model_path))
    exported = Path(model.export(format="onnx", imgsz=args.imgsz))
    target = args.output.resolve() if args.output else model_path.with_suffix(".onnx")
    if exported.resolve() != target:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(exported, target)
    print(f"exported ONNX to {target}")


if __name__ == "__main__":
    main()
