from __future__ import annotations

import argparse
import random
from pathlib import Path

import cv2
import yaml


IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".bmp", ".webp"]


def load_names(dataset_yaml: Path) -> dict[int, str]:
    with dataset_yaml.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    return {int(key): value for key, value in data["names"].items()}


def resolve_image(images_dir: Path, stem: str) -> Path:
    for ext in IMAGE_EXTENSIONS:
        candidate = images_dir / f"{stem}{ext}"
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"no image found for {stem}")


def draw_label_file(image_path: Path, label_path: Path, names: dict[int, str], output_path: Path) -> None:
    image = cv2.imread(str(image_path))
    if image is None:
        raise RuntimeError(f"failed to read image: {image_path}")

    height, width = image.shape[:2]
    content = label_path.read_text(encoding="utf-8").strip()
    if content:
        for line in content.splitlines():
            class_id, cx, cy, box_w, box_h = line.split()
            class_id = int(class_id)
            cx, cy, box_w, box_h = map(float, (cx, cy, box_w, box_h))
            x1 = int((cx - box_w / 2.0) * width)
            y1 = int((cy - box_h / 2.0) * height)
            x2 = int((cx + box_w / 2.0) * width)
            y2 = int((cy + box_h / 2.0) * height)
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 255), 2)
            cv2.putText(image, names[class_id], (x1, max(0, y1 - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output_path), image)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render YOLO labels back onto images for spot checks.")
    parser.add_argument("--dataset-root", type=Path, default=Path("datasets/bdd100k"))
    parser.add_argument("--dataset-yaml", type=Path, default=Path("configs/dataset_bdd100k.yaml"))
    parser.add_argument("--split", default="val")
    parser.add_argument("--count", type=int, default=16)
    parser.add_argument("--output-dir", type=Path, default=Path("results/visualize"))
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    names = load_names(args.dataset_yaml.resolve())
    labels_dir = (args.dataset_root / "labels" / args.split).resolve()
    images_dir = (args.dataset_root / "images" / args.split).resolve()
    label_files = sorted(labels_dir.glob("*.txt"))
    random.Random(args.seed).shuffle(label_files)

    for label_path in label_files[: args.count]:
        image_path = resolve_image(images_dir, label_path.stem)
        draw_label_file(image_path, label_path, names, (args.output_dir / f"{label_path.stem}.jpg").resolve())

    print(f"saved {min(args.count, len(label_files))} visualizations to {args.output_dir.resolve()}")


if __name__ == "__main__":
    main()

