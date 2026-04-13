from __future__ import annotations

import argparse
import shutil
from pathlib import Path
import sys
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import yaml
from ultralytics import YOLO

DEFAULT_CONFIG_PATH = PROJECT_ROOT / "configs" / "default.yaml"
DEFAULT_DATASET_CONFIG = PROJECT_ROOT / "configs" / "dataset_idd_animal.yaml"


def load_project_config(config_path: Path) -> dict[str, Any]:
    with config_path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def resolve_model_source(config: dict[str, Any]) -> str:
    model_name = str(config.get("obstacle_model", "yolo11n.pt"))
    in_weights_dir = PROJECT_ROOT / "weights" / model_name
    if in_weights_dir.exists():
        return str(in_weights_dir)
    in_root = PROJECT_ROOT / model_name
    if in_root.exists():
        return str(in_root)
    return model_name


def resolve_base_weights(config: dict[str, Any]) -> str | None:
    weight_name = str(config.get("obstacle_base", "")).strip()
    if not weight_name:
        return None
    in_weights_dir = PROJECT_ROOT / "weights" / weight_name
    if in_weights_dir.exists():
        return str(in_weights_dir)
    in_root = PROJECT_ROOT / weight_name
    if in_root.exists():
        return str(in_root)
    return weight_name


def canonical_weight_path() -> Path:
    return PROJECT_ROOT / "weights" / "animal_best.pt"


def build_training_model(config: dict[str, Any]) -> YOLO:
    model_source = resolve_model_source(config)
    base_weights = resolve_base_weights(config)
    model = YOLO(model_source)
    if base_weights and Path(base_weights).name != Path(model_source).name:
        model = model.load(base_weights)
    return model


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train the IDD single-class animal detection model.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    parser.add_argument("--quick", action="store_true", help="Run a 2-epoch smoke-training pass.")
    parser.add_argument("--epochs", type=int)
    parser.add_argument("--batch", type=int)
    parser.add_argument("--workers", type=int)
    parser.add_argument("--device")
    parser.add_argument("--name", default="train_animal")
    parser.add_argument("--imgsz", type=int)
    parser.add_argument("--fraction", type=float)
    return parser.parse_args()


def resolve_training_params(config: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    if args.quick:
        params = {
            "epochs": 2,
            "imgsz": 640,
            "batch": 8,
            "workers": 0,
            "fraction": 0.1,
            "amp": False,
        }
    else:
        params = {
            "epochs": int(config.get("obstacle_epochs", 100)),
            "imgsz": int(config.get("obstacle_imgsz", 960)),
            "batch": int(config.get("obstacle_batch_size", 32)),
            "workers": int(config.get("obstacle_workers", 8)),
            "fraction": 1.0,
            "amp": False,
        }

    if args.epochs is not None:
        params["epochs"] = args.epochs
    if args.imgsz is not None:
        params["imgsz"] = args.imgsz
    if args.batch is not None:
        params["batch"] = args.batch
    if args.workers is not None:
        params["workers"] = args.workers
    if args.fraction is not None:
        params["fraction"] = args.fraction
    return params


def main() -> None:
    args = parse_args()
    config = load_project_config(args.config.resolve())
    training_params = resolve_training_params(config, args)

    model = build_training_model(config)
    results = model.train(
        data=str(DEFAULT_DATASET_CONFIG.resolve()),
        epochs=training_params["epochs"],
        imgsz=training_params["imgsz"],
        batch=training_params["batch"],
        workers=training_params["workers"],
        fraction=training_params["fraction"],
        optimizer="SGD",
        patience=int(config.get("obstacle_patience", 20)),
        amp=training_params["amp"],
        project=str((PROJECT_ROOT / config["paths"]["results_dir"]).resolve()),
        name=args.name,
        exist_ok=True,
        save=True,
        plots=True,
        device=args.device,
    )

    best_weight = Path(results.save_dir) / "weights" / "best.pt"
    if best_weight.exists():
        target = canonical_weight_path()
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(best_weight, target)
        print(f"copied best weight to {target}")


if __name__ == "__main__":
    main()
