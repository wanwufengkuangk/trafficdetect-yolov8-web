from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import yaml
from ultralytics import YOLO

from training.train_obstacle import canonical_weight_path

DEFAULT_CONFIG_PATH = PROJECT_ROOT / "configs" / "default.yaml"


def load_project_config(config_path: Path) -> dict[str, Any]:
    with config_path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run command-line prediction for the IDD animal detection model.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    parser.add_argument("--model", type=Path)
    parser.add_argument("--source", required=True)
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--iou", type=float, default=0.45)
    parser.add_argument("--imgsz", type=int)
    parser.add_argument("--device")
    parser.add_argument("--name", default="predict_animal")
    return parser.parse_args()


def resolve_model_path(args: argparse.Namespace) -> Path:
    if args.model:
        return args.model.resolve()
    return canonical_weight_path()


def main() -> None:
    args = parse_args()
    config = load_project_config(args.config.resolve())
    model_path = resolve_model_path(args)
    if not model_path.exists():
        raise FileNotFoundError(f"missing checkpoint: {model_path}")

    model = YOLO(str(model_path))
    model.predict(
        source=args.source,
        conf=args.conf,
        iou=args.iou,
        imgsz=args.imgsz or int(config.get("obstacle_imgsz", 960)),
        device=args.device,
        save=True,
        project=str((PROJECT_ROOT / config["paths"]["results_dir"]).resolve()),
        name=args.name,
        exist_ok=True,
        verbose=True,
    )


if __name__ == "__main__":
    main()
