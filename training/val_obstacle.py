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
DEFAULT_DATASET_CONFIG = PROJECT_ROOT / "configs" / "dataset_idd_animal.yaml"


def load_project_config(config_path: Path) -> dict[str, Any]:
    with config_path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate the IDD animal detection model.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    parser.add_argument("--model", type=Path)
    parser.add_argument("--imgsz", type=int)
    parser.add_argument("--batch", type=int)
    parser.add_argument("--device")
    parser.add_argument("--name", default="val_animal")
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
    metrics = model.val(
        data=str(DEFAULT_DATASET_CONFIG.resolve()),
        imgsz=args.imgsz or int(config.get("obstacle_imgsz", 960)),
        batch=args.batch or int(config.get("obstacle_batch_size", 32)),
        device=args.device,
        project=str((PROJECT_ROOT / config["paths"]["results_dir"]).resolve()),
        name=args.name,
        exist_ok=True,
    )
    print(f"validated {model_path.name}")
    print(f"mAP50-95(box)={metrics.box.map:.4f}")
    print(f"mAP50(box)={metrics.box.map50:.4f}")


if __name__ == "__main__":
    main()
