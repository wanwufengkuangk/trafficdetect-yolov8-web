from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from data.bdd100k_to_yolo import link_or_copy_split


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare RoadObstacle21 images for robustness evaluation.")
    parser.add_argument("--source-root", type=Path, required=True, help="Path to raw dataset_ObstacleTrack directory.")
    parser.add_argument("--dataset-root", type=Path, default=Path("datasets/obstacle21"))
    parser.add_argument("--images-mode", choices=["junction", "copy"], default="junction")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source_images = args.source_root.resolve() / "images"
    target_images = args.dataset_root.resolve() / "images"
    link_or_copy_split(source_images, target_images, mode=args.images_mode)

    image_count = sum(1 for path in source_images.iterdir() if path.is_file())
    mask_count = sum(1 for path in (args.source_root.resolve() / "labels_masks").glob("*"))
    print(f"prepared obstacle21 images={image_count} masks={mask_count} target={target_images}")


if __name__ == "__main__":
    main()
