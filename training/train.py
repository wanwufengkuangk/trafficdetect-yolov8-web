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

from models.register import register_all

DEFAULT_CONFIG_PATH = PROJECT_ROOT / "configs" / "default.yaml"

VARIANT_TO_MODEL = {
    "baseline": "yolov8s.yaml",
    "p2": "configs/model_yolov8s_p2.yaml",
    "p2_cbam": "configs/model_yolov8s_custom.yaml",
    "full": "configs/model_yolov8s_custom.yaml",
}

VARIANT_TO_WEIGHT_NAME = {
    "baseline": "baseline_best.pt",
    "p2": "p2_best.pt",
    "p2_cbam": "p2_cbam_best.pt",
    "full": "best.pt",
}


def load_project_config(config_path: Path) -> dict[str, Any]:
    with config_path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def resolve_model_source(config: dict[str, Any], variant: str) -> str:
    model_name = VARIANT_TO_MODEL[variant]
    candidate = PROJECT_ROOT / model_name
    if candidate.exists():
        return str(candidate)
    return model_name


def resolve_base_weights(config: dict[str, Any]) -> str:
    base_weight_name = config["model"]["base"]
    candidate = PROJECT_ROOT / "weights" / base_weight_name
    if candidate.exists():
        return str(candidate)
    return base_weight_name


def canonical_weight_path(variant: str) -> Path:
    return PROJECT_ROOT / "weights" / VARIANT_TO_WEIGHT_NAME[variant]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train baseline or improved YOLOv8 variants on the rebuilt BDD100K dataset.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    parser.add_argument("--variant", choices=["baseline", "p2", "p2_cbam", "full"], default="baseline")
    parser.add_argument("--quick", action="store_true", help="Run the quick smoke-training pass.")
    parser.add_argument("--epochs", type=int)
    parser.add_argument("--batch", type=int)
    parser.add_argument("--workers", type=int)
    parser.add_argument("--device")
    parser.add_argument("--name")
    parser.add_argument("--imgsz", type=int)
    parser.add_argument("--fraction", type=float, default=1.0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_project_config(args.config.resolve())

    if args.variant in {"p2_cbam", "full"}:
        register_all(use_wiou=args.variant == "full")

    model = YOLO(resolve_model_source(config, args.variant)).load(resolve_base_weights(config))

    epochs = args.epochs if args.epochs is not None else (config["training"]["quick_epochs"] if args.quick else config["training"]["epochs"])
    batch = args.batch if args.batch is not None else config["training"]["batch_size"]
    workers = args.workers if args.workers is not None else config["training"]["workers"]
    run_name = args.name or f"train_{args.variant}{'_quick' if args.quick else ''}"
    imgsz = args.imgsz if args.imgsz is not None else config["model"]["input_size"]

    results = model.train(
        data=str((PROJECT_ROOT / "configs" / "dataset_bdd100k.yaml").resolve()),
        epochs=epochs,
        batch=batch,
        imgsz=imgsz,
        optimizer=config["training"]["optimizer"],
        lr0=config["training"]["lr0"],
        lrf=config["training"]["lrf"],
        momentum=config["training"]["momentum"],
        weight_decay=config["training"]["weight_decay"],
        warmup_epochs=config["training"]["warmup_epochs"],
        cos_lr=config["training"]["cos_lr"],
        amp=config["training"]["amp"],
        patience=config["training"]["patience"],
        workers=workers,
        close_mosaic=config["training"]["close_mosaic"],
        mosaic=config["augmentation"]["mosaic"],
        mixup=config["augmentation"]["mixup"],
        copy_paste=config["augmentation"]["copy_paste"],
        hsv_h=config["augmentation"]["hsv_h"],
        hsv_s=config["augmentation"]["hsv_s"],
        hsv_v=config["augmentation"]["hsv_v"],
        translate=config["augmentation"]["translate"],
        scale=config["augmentation"]["scale"],
        fliplr=config["augmentation"]["fliplr"],
        erasing=config["augmentation"]["erasing"],
        project=str((PROJECT_ROOT / config["paths"]["results_dir"]).resolve()),
        name=run_name,
        exist_ok=True,
        plots=True,
        save=True,
        device=args.device,
        fraction=args.fraction,
    )

    save_dir = Path(results.save_dir)
    best_weight = save_dir / "weights" / "best.pt"
    if best_weight.exists():
        target = canonical_weight_path(args.variant)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(best_weight, target)
        print(f"copied best weight to {target}")


if __name__ == "__main__":
    main()
