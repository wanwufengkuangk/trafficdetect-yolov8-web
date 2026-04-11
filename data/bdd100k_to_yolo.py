from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


BDD100K_CLASS_MAP: dict[str, int] = {
    "pedestrian": 0,
    "rider": 1,
    "car": 2,
    "truck": 3,
    "bus": 4,
    "train": 5,
    "motorcycle": 6,
    "bicycle": 7,
    "traffic light": 8,
    "traffic sign": 9,
}

BDD100K_CATEGORY_ALIASES: dict[str, str] = {
    "person": "pedestrian",
    "pedestrian": "pedestrian",
    "rider": "rider",
    "car": "car",
    "truck": "truck",
    "bus": "bus",
    "train": "train",
    "motor": "motorcycle",
    "motorcycle": "motorcycle",
    "bike": "bicycle",
    "bicycle": "bicycle",
    "traffic light": "traffic light",
    "traffic sign": "traffic sign",
}


@dataclass(frozen=True)
class ConversionResult:
    file_stem: str
    yolo_rows: list[str]
    class_counts: dict[str, int]
    total_objects: int
    mapped_objects: int


@dataclass(frozen=True)
class SplitSummary:
    split: str
    image_count: int
    label_count: int
    empty_label_files: int
    total_boxes: int
    class_counts: dict[str, int]


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(value, upper))


def convert_box2d_to_yolo(
    box2d: dict[str, float],
    image_width: int = 1280,
    image_height: int = 720,
) -> tuple[float, float, float, float]:
    x1 = clamp(float(box2d["x1"]), 0.0, float(image_width))
    y1 = clamp(float(box2d["y1"]), 0.0, float(image_height))
    x2 = clamp(float(box2d["x2"]), 0.0, float(image_width))
    y2 = clamp(float(box2d["y2"]), 0.0, float(image_height))
    if x2 <= x1 or y2 <= y1:
        raise ValueError("invalid box2d coordinates after clamping")

    center_x = ((x1 + x2) / 2.0) / image_width
    center_y = ((y1 + y2) / 2.0) / image_height
    width = (x2 - x1) / image_width
    height = (y2 - y1) / image_height
    return (
        round(center_x, 6),
        round(center_y, 6),
        round(width, 6),
        round(height, 6),
    )


def iter_frame_objects(record: dict) -> Iterable[dict]:
    for frame in record.get("frames", []):
        for obj in frame.get("objects", []):
            yield obj


def convert_annotation_record(
    record: dict,
    image_width: int = 1280,
    image_height: int = 720,
) -> ConversionResult:
    class_counts: Counter[str] = Counter()
    yolo_rows: list[str] = []
    total_objects = 0

    for obj in iter_frame_objects(record):
        total_objects += 1
        category = obj.get("category")
        canonical_category = BDD100K_CATEGORY_ALIASES.get(category or "")
        box2d = obj.get("box2d")
        if canonical_category not in BDD100K_CLASS_MAP or not box2d:
            continue
        try:
            cx, cy, width, height = convert_box2d_to_yolo(
                box2d=box2d,
                image_width=image_width,
                image_height=image_height,
            )
        except ValueError:
            continue
        class_counts[canonical_category] += 1
        yolo_rows.append(
            f"{BDD100K_CLASS_MAP[canonical_category]} {cx:.6f} {cy:.6f} {width:.6f} {height:.6f}"
        )

    return ConversionResult(
        file_stem=record["name"],
        yolo_rows=yolo_rows,
        class_counts=dict(class_counts),
        total_objects=total_objects,
        mapped_objects=sum(class_counts.values()),
    )


def load_annotation(json_path: Path) -> dict:
    with json_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def link_or_copy_split(source_dir: Path, target_dir: Path, mode: str = "junction") -> None:
    if target_dir.exists():
        if target_dir.is_symlink():
            if target_dir.resolve() == source_dir.resolve():
                return
            target_dir.unlink()
        elif any(target_dir.iterdir()):
            return
        else:
            target_dir.rmdir()

    if mode == "copy":
        shutil.copytree(source_dir, target_dir, dirs_exist_ok=True)
        return

    if mode == "junction":
        target_dir.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(target_dir), str(source_dir)],
            check=True,
            capture_output=True,
            text=True,
        )
        return

    raise ValueError(f"unsupported images mode: {mode}")


def materialize_split_images(source_dir: Path, target_dir: Path, mode: str = "hardlink") -> int:
    target_dir.mkdir(parents=True, exist_ok=True)
    created = 0
    for image_path in sorted(path for path in source_dir.iterdir() if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS):
        target_path = target_dir / image_path.name
        if target_path.exists():
            continue
        if mode == "hardlink":
            os.link(image_path, target_path)
        elif mode == "copy":
            shutil.copy2(image_path, target_path)
        else:
            raise ValueError(f"unsupported images mode: {mode}")
        created += 1
    return created


def convert_split(
    source_root: Path,
    dataset_root: Path,
    split: str,
    image_width: int = 1280,
    image_height: int = 720,
    images_mode: str = "hardlink",
) -> SplitSummary:
    source_dir = source_root / split
    labels_dir = dataset_root / "labels" / split
    images_dir = dataset_root / "images" / split
    labels_dir.mkdir(parents=True, exist_ok=True)
    materialize_split_images(source_dir=source_dir, target_dir=images_dir, mode=images_mode)

    class_counts: Counter[str] = Counter()
    empty_label_files = 0
    total_boxes = 0
    label_count = 0
    image_count = 0

    for json_path in sorted(source_dir.glob("*.json")):
        record = load_annotation(json_path)
        converted = convert_annotation_record(
            record,
            image_width=image_width,
            image_height=image_height,
        )
        (labels_dir / f"{converted.file_stem}.txt").write_text(
            "\n".join(converted.yolo_rows),
            encoding="utf-8",
        )

        if (source_dir / f"{converted.file_stem}.jpg").exists():
            image_count += 1
        label_count += 1
        total_boxes += len(converted.yolo_rows)
        if not converted.yolo_rows:
            empty_label_files += 1
        class_counts.update(converted.class_counts)

    return SplitSummary(
        split=split,
        image_count=image_count,
        label_count=label_count,
        empty_label_files=empty_label_files,
        total_boxes=total_boxes,
        class_counts=dict(class_counts),
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert BDD100K per-image JSON labels to YOLO TXT format.")
    parser.add_argument("--source-root", type=Path, required=True, help="Path to BDD100K 100k root containing train/val.")
    parser.add_argument("--dataset-root", type=Path, default=Path("datasets/bdd100k"), help="Output dataset root.")
    parser.add_argument("--splits", nargs="+", default=["train", "val"], help="Dataset splits to convert.")
    parser.add_argument("--image-width", type=int, default=1280)
    parser.add_argument("--image-height", type=int, default=720)
    parser.add_argument("--images-mode", choices=["hardlink", "copy"], default="hardlink")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    dataset_root = args.dataset_root.resolve()
    summaries: list[SplitSummary] = []
    for split in args.splits:
        summaries.append(
            convert_split(
                source_root=args.source_root.resolve(),
                dataset_root=dataset_root,
                split=split,
                image_width=args.image_width,
                image_height=args.image_height,
                images_mode=args.images_mode,
            )
        )

    for summary in summaries:
        print(
            f"[{summary.split}] images={summary.image_count} labels={summary.label_count} "
            f"empty={summary.empty_label_files} boxes={summary.total_boxes}"
        )
        for class_name, count in sorted(summary.class_counts.items(), key=lambda item: item[0]):
            print(f"  - {class_name}: {count}")


if __name__ == "__main__":
    main()
