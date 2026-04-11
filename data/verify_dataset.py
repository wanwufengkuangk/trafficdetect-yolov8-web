from __future__ import annotations

import argparse
import sys
from pathlib import Path


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def collect_image_stems(images_dir: Path) -> set[str]:
    return {path.stem for path in images_dir.iterdir() if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS}


def collect_label_stems(labels_dir: Path) -> set[str]:
    return {path.stem for path in labels_dir.glob("*.txt")}


def verify_split(dataset_root: Path, split: str) -> bool:
    images_dir = dataset_root / "images" / split
    labels_dir = dataset_root / "labels" / split
    if not images_dir.exists() or not labels_dir.exists():
        print(f"[{split}] missing directory: images={images_dir.exists()} labels={labels_dir.exists()}")
        return False

    image_stems = collect_image_stems(images_dir)
    label_stems = collect_label_stems(labels_dir)
    empty_labels = sum(1 for path in labels_dir.glob("*.txt") if not path.read_text(encoding="utf-8").strip())

    missing_labels = sorted(image_stems - label_stems)
    missing_images = sorted(label_stems - image_stems)

    print(
        f"[{split}] images={len(image_stems)} labels={len(label_stems)} "
        f"empty_labels={empty_labels} missing_labels={len(missing_labels)} missing_images={len(missing_images)}"
    )
    if missing_labels:
        print(f"  missing labels sample: {missing_labels[:10]}")
    if missing_images:
        print(f"  missing images sample: {missing_images[:10]}")

    return not missing_labels and not missing_images


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify image/label completeness for the rebuilt BDD100K dataset.")
    parser.add_argument("--dataset-root", type=Path, default=Path("datasets/bdd100k"))
    parser.add_argument("--splits", nargs="+", default=["train", "val"])
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ok = True
    for split in args.splits:
        ok = verify_split(args.dataset_root.resolve(), split) and ok
    if not ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

